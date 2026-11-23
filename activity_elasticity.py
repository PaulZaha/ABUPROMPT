"""Test saved LLM duration estimates one at a time at half and double their values.

Usage:
    python activity_elasticity.py
    python activity_elasticity.py --workbook runs_eval/<run>/results.xlsx

The script does not call an LLM. Custom goals are not reported as numeric KPIs
by the existing evaluator, so the output marks their quantitative result as
unavailable.
"""

import argparse
import ast
import json
import math
import os
import posixpath
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from zipfile import ZipFile

import numpy as np
import pandas as pd
import pm4py

from evaluator import evaluator_simulation, sim_probabilities
from evaluator.cost import cost_evaluator
from preparer import bpmn_preparation, evaluator_preparation


SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
PERTURBATION_FACTORS = (0.5, 2.0)
SIMULATION_COUNT = 10_000


def _column_index(cell_reference: str) -> int:
    column = 0
    for character in cell_reference:
        if not character.isalpha():
            break
        column = column * 26 + ord(character.upper()) - ord("A") + 1
    return column - 1


def _cell_value(cell: ET.Element, shared_strings: List[str]) -> object:
    value_node = cell.find(f"{{{SPREADSHEET_NS}}}v")
    cell_type = cell.get("t")

    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(f".//{{{SPREADSHEET_NS}}}t"))
    if value_node is None:
        return None

    value = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(value)]
    if cell_type in ("str", "e"):
        return value
    if cell_type == "b":
        return value == "1"
    if not value:
        return None

    try:
        number = float(value)
    except ValueError:
        return value
    return int(number) if number.is_integer() else number


def read_xlsx_sheet(path: Path, sheet_name: str = "results") -> pd.DataFrame:
    """Read a worksheet using the standard library, without an Excel reader dependency."""
    with ZipFile(path) as workbook:
        names = set(workbook.namelist())
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(node.text or "" for node in item.findall(f".//{{{SPREADSHEET_NS}}}t"))
                for item in root.findall(f"{{{SPREADSHEET_NS}}}si")
            ]

        workbook_root = ET.fromstring(workbook.read("xl/workbook.xml"))
        relationships_root = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        relationships = {
            relation.get("Id"): relation.get("Target")
            for relation in relationships_root.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
        }
        worksheets = workbook_root.findall(f".//{{{SPREADSHEET_NS}}}sheet")
        selected_sheet = next(
            (sheet for sheet in worksheets if sheet.get("name") == sheet_name),
            worksheets[0] if worksheets else None,
        )
        if selected_sheet is None:
            raise ValueError(f"No worksheets found in workbook: {path}")

        relationship_id = selected_sheet.get(f"{{{OFFICE_REL_NS}}}id")
        target = relationships.get(relationship_id)
        if not target:
            raise ValueError(f"Could not find worksheet XML for '{selected_sheet.get('name')}'")
        target = target.lstrip("/")
        worksheet_path = (
            target if target.startswith("xl/") else posixpath.normpath(posixpath.join("xl", target))
        )
        worksheet_root = ET.fromstring(workbook.read(worksheet_path))
        xml_rows = worksheet_root.findall(f".//{{{SPREADSHEET_NS}}}sheetData/{{{SPREADSHEET_NS}}}row")

        matrix: List[List[object]] = []
        for xml_row in xml_rows:
            cells = xml_row.findall(f"{{{SPREADSHEET_NS}}}c")
            row_values: List[object] = []
            for cell in cells:
                index = _column_index(cell.get("r", ""))
                if index >= len(row_values):
                    row_values.extend([None] * (index + 1 - len(row_values)))
                row_values[index] = _cell_value(cell, shared_strings)
            matrix.append(row_values)

    if not matrix:
        raise ValueError(f"Worksheet '{selected_sheet.get('name')}' is empty: {path}")

    headers = [str(value) if value is not None else "" for value in matrix[0]]
    records = []
    for values in matrix[1:]:
        padded = values + [None] * max(0, len(headers) - len(values))
        if any(value is not None for value in padded):
            records.append(dict(zip(headers, padded)))
    return pd.DataFrame.from_records(records, columns=headers)


def find_workbook(root: Path) -> Path:
    candidates = []
    for pattern in (
        "runs_eval/**/evaluation_results_gpt5.xlsx",
        "runs_eval/**/evaluation_results_gp5.xlsx",
        "runs_eval/**/evaluation-results_gp5.xlsx",
    ):
        candidates.extend(root.glob(pattern))
    if not candidates:
        raise FileNotFoundError(
            "Could not locate evaluation_results_gpt5.xlsx under runs_eval; "
            "pass the workbook path with --workbook."
        )
    return max(candidates, key=lambda candidate: candidate.stat().st_mtime)


def parse_estimates(value: object, field_name: str, workbook_row: int) -> Dict[str, float]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return {}
    if isinstance(value, dict):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise ValueError(
                f"Invalid {field_name} at workbook row {workbook_row}: {value!r}"
            ) from exc
    else:
        raise ValueError(
            f"Expected a dictionary in {field_name} at workbook row {workbook_row}, "
            f"got {type(value).__name__}"
        )
    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} at workbook row {workbook_row} is not a dictionary")

    estimates: Dict[str, float] = {}
    for activity, estimate in parsed.items():
        try:
            number = float(estimate)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid estimate for {activity!r} in {field_name} "
                f"at workbook row {workbook_row}: {estimate!r}"
            ) from exc
        if not math.isfinite(number) or number < 0:
            raise ValueError(
                f"Estimate for {activity!r} in {field_name} at workbook row "
                f"{workbook_row} must be finite and non-negative"
            )
        estimates[str(activity)] = number
    return estimates


def build_duration_table(
    significant_durations: pd.DataFrame,
    estimates: Dict[str, float],
    factor: float,
    bpmn,
) -> pd.DataFrame:
    durations = significant_durations.copy(deep=True)
    durations["weighted_significant_duration"] = pd.to_numeric(
        durations["weighted_significant_duration"], errors="coerce"
    )
    for activity, estimate in estimates.items():
        matches = durations["activity"] == activity
        if matches.any():
            durations.loc[matches, "weighted_significant_duration"] = estimate * factor
        else:
            durations = pd.concat(
                [
                    durations,
                    pd.DataFrame(
                        {
                            "activity": [activity],
                            "weighted_significant_duration": [estimate * factor],
                        }
                    ),
                ],
                ignore_index=True,
            )

    task_names = [
        node.name
        for node in bpmn.get_nodes()
        if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Task)
    ]
    missing = [
        name
        for name in task_names
        if not (
            (durations["activity"] == name)
            & durations["weighted_significant_duration"].notna()
        ).any()
    ]
    if missing:
        raise ValueError(
            "No saved duration estimate is available for BPMN task(s): "
            + ", ".join(sorted(set(missing)))
        )
    return durations


def simulate_scenario(
    bpmn_path: Path,
    log,
    log_activities: Iterable[str],
    significant_durations: pd.DataFrame,
    estimates: Dict[str, float],
    factor: float,
) -> pd.DataFrame:
    bpmn = bpmn_preparation.prepare_bpmn(pm4py.read_bpmn(str(bpmn_path)))
    durations = build_duration_table(significant_durations, estimates, factor, bpmn)
    new_activities = evaluator_simulation.get_new_activities(bpmn, log_activities)
    probabilities = sim_probabilities.get_gateway_probabilities(bpmn, log, new_activities)
    return evaluator_simulation.run_simulation(
        bpmn,
        probabilities,
        new_activities,
        durations,
    )


def scenario_metrics(
    raw_results: pd.DataFrame,
    durations: pd.DataFrame,
    costs: Optional[Dict[str, float]],
) -> Dict[str, Optional[float]]:
    mean_duration = float(raw_results["duration"].mean())
    duration_by_activity = dict(
        zip(durations["activity"], durations["weighted_significant_duration"])
    )
    adjusted_durations = []
    for _, row in raw_results.iterrows():
        first_activity = row["trace"][0]
        first_duration = float(duration_by_activity[first_activity])
        adjusted_durations.append(row["duration"] - min(first_duration, row["duration"]))

    mean_cost: Optional[float] = None
    if costs is not None:
        cost_total = 0.0
        unique_durations = raw_results.drop_duplicates(subset="duration")
        for _, row in unique_durations.iterrows():
            trace_cost = sum(costs[activity] for activity in row["trace"])
            percentage = (raw_results["duration"] == row["duration"]).mean()
            cost_total += trace_cost * percentage
        mean_cost = float(cost_total)

    return {
        "estimated_duration": mean_duration,
        "adjusted_duration": float(np.mean(adjusted_durations)),
        "estimated_cost": mean_cost,
    }


def optional_number(row: pd.Series, column: str) -> Optional[float]:
    value = row.get(column)
    if value is None or pd.isna(value):
        return None
    return float(value)


def ratio(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def make_cost_map(row: pd.Series, workbook_row: int) -> Optional[Dict[str, float]]:
    if optional_number(row, "Estimated cost [€]") is None:
        return None
    estimates = parse_estimates(row.get("LLM cost estimates (new)"), "LLM cost estimates (new)", workbook_row)
    costs = {**cost_evaluator.get_defined_costs(), **estimates}
    return costs


def load_config(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return config


def elasticity(
    scenario_value: Optional[float],
    reference_value: Optional[float],
    factor: float,
    input_estimate: Optional[float],
) -> Optional[float]:
    if (
        scenario_value is None
        or reference_value in (None, 0)
        or factor == 1.0
        or input_estimate in (None, 0)
    ):
        return None
    input_change_percent = (factor - 1.0) * 100
    output_change_percent = (scenario_value - reference_value) / abs(reference_value) * 100
    return output_change_percent / input_change_percent


def scale_one_estimate(
    estimates: Dict[str, float],
    activity: str,
    factor: float,
) -> Dict[str, float]:
    scaled = estimates.copy()
    scaled[activity] *= factor
    return scaled


def make_output_row(
    item: dict,
    estimate_source: str,
    activity: Optional[str],
    input_estimate: Optional[float],
    factor: float,
    baseline_metrics: Dict[str, Optional[float]],
    improved_metrics: Dict[str, Optional[float]],
    baseline_control: Dict[str, Optional[float]],
    improved_control: Dict[str, Optional[float]],
) -> dict:
    reference = item["row"]
    time_change = ratio(
        (
            baseline_metrics["estimated_duration"] - improved_metrics["estimated_duration"]
            if baseline_metrics["estimated_duration"] is not None
            and improved_metrics["estimated_duration"] is not None
            else None
        ),
        baseline_metrics["estimated_duration"],
    )
    control_time_change = ratio(
        (
            baseline_control["estimated_duration"] - improved_control["estimated_duration"]
            if baseline_control["estimated_duration"] is not None
            and improved_control["estimated_duration"] is not None
            else None
        ),
        baseline_control["estimated_duration"],
    )
    cost_change = ratio(
        (
            baseline_metrics["estimated_cost"] - improved_metrics["estimated_cost"]
            if baseline_metrics["estimated_cost"] is not None
            and improved_metrics["estimated_cost"] is not None
            else None
        ),
        baseline_metrics["estimated_cost"],
    )
    control_cost_change = ratio(
        (
            baseline_control["estimated_cost"] - improved_control["estimated_cost"]
            if baseline_control["estimated_cost"] is not None
            and improved_control["estimated_cost"] is not None
            else None
        ),
        baseline_control["estimated_cost"],
    )
    time_change_percent = time_change * 100 if time_change is not None else None
    control_time_change_percent = (
        control_time_change * 100 if control_time_change is not None else None
    )
    cost_change_percent = cost_change * 100 if cost_change is not None else None
    control_cost_change_percent = (
        control_cost_change * 100 if control_cost_change is not None else None
    )
    adjusted_time_change = ratio(
        (
            baseline_metrics["adjusted_duration"] - improved_metrics["adjusted_duration"]
            if baseline_metrics["adjusted_duration"] is not None
            and improved_metrics["adjusted_duration"] is not None
            else None
        ),
        baseline_metrics["adjusted_duration"],
    )

    return {
        "Workbook row": item["workbook_row"],
        "Dataset": item["dataset"],
        "Objective": item["objective"],
        "Iteration": item["iteration"],
        "Perturbed estimate source": estimate_source,
        "Perturbed activity": activity,
        "LLM estimate before [h]": input_estimate,
        "LLM estimate after [h]": (
            input_estimate * factor if input_estimate is not None else None
        ),
        "Requested estimate factor": factor,
        "Actual estimate change [%]": (
            (factor - 1.0) * 100 if input_estimate not in (None, 0) else 0.0
        ),
        "Estimated duration [h] (original model)": baseline_metrics["estimated_duration"],
        "Estimated duration [h] (improved model)": improved_metrics["estimated_duration"],
        "Estimated duration [h] (original, control)": baseline_control["estimated_duration"],
        "Estimated duration [h] (improved, control)": improved_control["estimated_duration"],
        "Estimated duration [h] (original, workbook)": optional_number(
            reference, "Estimated duration [h]"
        ),
        "Estimated duration [h] (improved, workbook)": optional_number(
            reference, "Estimated duration [h] (new)"
        ),
        "Adjusted duration [h] (original model)": baseline_metrics["adjusted_duration"],
        "Adjusted duration [h] (improved model)": improved_metrics["adjusted_duration"],
        "Adjusted duration [h] (original, control)": baseline_control["adjusted_duration"],
        "Adjusted duration [h] (improved, control)": improved_control["adjusted_duration"],
        "Adjusted duration [h] (original, workbook)": optional_number(
            reference, "Adjusted duration [h]"
        ),
        "Adjusted duration [h] (improved, workbook)": optional_number(
            reference, "Adjusted duration [h] (new)"
        ),
        "Duration elasticity (original model)": elasticity(
            baseline_metrics["estimated_duration"],
            baseline_control["estimated_duration"],
            factor,
            input_estimate,
        ),
        "Duration elasticity (improved model)": elasticity(
            improved_metrics["estimated_duration"],
            improved_control["estimated_duration"],
            factor,
            input_estimate,
        ),
        "Adjusted-duration elasticity (original model)": elasticity(
            baseline_metrics["adjusted_duration"],
            baseline_control["adjusted_duration"],
            factor,
            input_estimate,
        ),
        "Adjusted-duration elasticity (improved model)": elasticity(
            improved_metrics["adjusted_duration"],
            improved_control["adjusted_duration"],
            factor,
            input_estimate,
        ),
        "Process time change [%] (scenario)": time_change_percent,
        "Process time change [%] (control)": control_time_change_percent,
        "Process time change [%] (workbook)": optional_number(
            reference, "Process time change [%]"
        ),
        "Process time change delta [percentage points]": (
            time_change_percent - control_time_change_percent
            if time_change_percent is not None and control_time_change_percent is not None
            else None
        ),
        "Adjusted process time change [%] (scenario)": (
            adjusted_time_change * 100 if adjusted_time_change is not None else None
        ),
        "Time-improvement elasticity": elasticity(
            time_change_percent,
            control_time_change_percent,
            factor,
            input_estimate,
        ),
        "Estimated cost [€] (original model)": baseline_metrics["estimated_cost"],
        "Estimated cost [€] (improved model)": improved_metrics["estimated_cost"],
        "Estimated cost [€] (original, control)": baseline_control["estimated_cost"],
        "Estimated cost [€] (improved, control)": improved_control["estimated_cost"],
        "Estimated cost [€] (improved, workbook)": optional_number(
            reference, "Estimated cost [€] (new)"
        ),
        "Cost elasticity (original model)": elasticity(
            baseline_metrics["estimated_cost"],
            baseline_control["estimated_cost"],
            factor,
            input_estimate,
        ),
        "Cost elasticity (improved model)": elasticity(
            improved_metrics["estimated_cost"],
            improved_control["estimated_cost"],
            factor,
            input_estimate,
        ),
        "Process cost change [%] (scenario)": cost_change_percent,
        "Process cost change [%] (control)": control_cost_change_percent,
        "Process cost change [%] (workbook)": optional_number(
            reference, "Process cost change [%]"
        ),
        "Process cost change delta [percentage points]": (
            cost_change_percent - control_cost_change_percent
            if cost_change_percent is not None and control_cost_change_percent is not None
            else None
        ),
        "Cost-improvement elasticity": elasticity(
            cost_change_percent,
            control_cost_change_percent,
            factor,
            input_estimate,
        ),
        "Custom goal": item["custom_goal"],
        "Custom metric": None,
        "Custom metric status": (
            "Not available: the evaluator records custom goals as prompt text, "
            "not as a numeric KPI."
        ),
    }


def run(workbook_path: Path, data_dir: Path, config_path: Path, output_path: Path) -> pd.DataFrame:
    results = read_xlsx_sheet(workbook_path)
    required_columns = {
        "Dataset",
        "Objective",
        "Iteration",
        "LLM duration estimates (original)",
        "LLM duration estimates (new)",
    }
    missing_columns = required_columns - set(results.columns)
    if missing_columns:
        raise ValueError(f"Workbook is missing required columns: {', '.join(sorted(missing_columns))}")
    if results.empty:
        raise ValueError(f"No evaluation results found in {workbook_path}")

    config = load_config(config_path)
    dataset_config = config.get("datasets", {})
    if not isinstance(dataset_config, dict):
        raise ValueError(f"'datasets' in {config_path} must be a JSON object")

    parsed_rows = []
    for index, row in results.iterrows():
        workbook_row = index + 2
        dataset = str(row["Dataset"])
        objective = str(row["Objective"])
        iteration = int(row["Iteration"])
        iteration_dir = workbook_path.parent / dataset / objective / f"iter-{iteration:02d}"
        input_bpmn = iteration_dir / "input.bpmn"
        improved_bpmn = iteration_dir / "improved.bpmn"
        for required_path in (input_bpmn, improved_bpmn):
            if not required_path.is_file():
                raise FileNotFoundError(
                    f"Workbook row {workbook_row} points to a missing model: {required_path}"
                )
        dataset_dir = data_dir / dataset
        xes_path = next(
            (path for path in sorted(dataset_dir.iterdir()) if path.is_file() and path.suffix.lower() == ".xes"),
            None,
        )
        if xes_path is None:
            raise FileNotFoundError(f"No .xes event log found in {dataset_dir}")

        parsed_rows.append(
            {
                "source_index": index,
                "workbook_row": workbook_row,
                "row": row,
                "dataset": dataset,
                "objective": objective,
                "iteration": iteration,
                "iteration_dir": iteration_dir,
                "input_bpmn": input_bpmn,
                "improved_bpmn": improved_bpmn,
                "xes_path": xes_path,
                "original_estimates": parse_estimates(
                    row.get("LLM duration estimates (original)"),
                    "LLM duration estimates (original)",
                    workbook_row,
                ),
                "new_estimates": parse_estimates(
                    row.get("LLM duration estimates (new)"),
                    "LLM duration estimates (new)",
                    workbook_row,
                ),
                "costs": make_cost_map(row, workbook_row),
                "custom_goal": (
                    (dataset_config.get(dataset) or {}).get("custom_goal")
                    if isinstance(dataset_config.get(dataset) or {}, dict)
                    else None
                ),
            }
        )

    rows_by_dataset: Dict[str, List[dict]] = {}
    for item in parsed_rows:
        rows_by_dataset.setdefault(item["dataset"], []).append(item)

    output_rows = []
    with tempfile.TemporaryDirectory(prefix="activity_elasticity_") as temporary_dir:
        for dataset, items in rows_by_dataset.items():
            print(f"Preparing {dataset}: {len(items)} evaluation result(s)")
            log, log_activities, _, _, significant_durations = evaluator_preparation.prepare_log(
                str(items[0]["xes_path"]),
                temporary_dir,
            )

            original_estimates = items[0]["original_estimates"]
            baseline_control_raw = simulate_scenario(
                items[0]["input_bpmn"],
                log,
                log_activities,
                significant_durations,
                original_estimates,
                1.0,
            )
            baseline_control_durations = build_duration_table(
                significant_durations,
                original_estimates,
                1.0,
                bpmn_preparation.prepare_bpmn(pm4py.read_bpmn(str(items[0]["input_bpmn"]))),
            )
            baseline_perturbations = {}

            for item in items:
                baseline_control = scenario_metrics(
                    baseline_control_raw,
                    baseline_control_durations,
                    item["costs"],
                )
                improved_estimates = {**item["original_estimates"], **item["new_estimates"]}
                improved_control_raw = simulate_scenario(
                    item["improved_bpmn"],
                    log,
                    log_activities,
                    significant_durations,
                    improved_estimates,
                    1.0,
                )
                improved_control_durations = build_duration_table(
                    significant_durations,
                    improved_estimates,
                    1.0,
                    bpmn_preparation.prepare_bpmn(pm4py.read_bpmn(str(item["improved_bpmn"]))),
                )
                improved_control = scenario_metrics(
                    improved_control_raw,
                    improved_control_durations,
                    item["costs"],
                )

                perturbations = [
                    ("original model", activity, estimate)
                    for activity, estimate in item["original_estimates"].items()
                ] + [
                    ("improved model", activity, estimate)
                    for activity, estimate in item["new_estimates"].items()
                ]
                print(
                    f"  {item['objective']} iteration {item['iteration']}: "
                    f"{len(perturbations)} estimated activity/activities"
                )

                if not perturbations:
                    output_rows.append(
                        make_output_row(
                            item,
                            "none",
                            None,
                            None,
                            1.0,
                            baseline_control,
                            improved_control,
                            baseline_control,
                            improved_control,
                        )
                    )
                    continue

                for estimate_source, activity, estimate in perturbations:
                    for factor in PERTURBATION_FACTORS:
                        if estimate_source == "original model":
                            changed_original = scale_one_estimate(
                                item["original_estimates"],
                                activity,
                                factor,
                            )
                            if changed_original == item["original_estimates"]:
                                baseline_metrics = baseline_control
                            else:
                                baseline_key = (activity, factor)
                                if baseline_key not in baseline_perturbations:
                                    baseline_raw = simulate_scenario(
                                        item["input_bpmn"],
                                        log,
                                        log_activities,
                                        significant_durations,
                                        changed_original,
                                        1.0,
                                    )
                                    baseline_durations = build_duration_table(
                                        significant_durations,
                                        changed_original,
                                        1.0,
                                        bpmn_preparation.prepare_bpmn(
                                            pm4py.read_bpmn(str(item["input_bpmn"]))
                                        ),
                                    )
                                    baseline_perturbations[baseline_key] = (
                                        baseline_raw,
                                        baseline_durations,
                                    )
                                baseline_raw, baseline_durations = baseline_perturbations[baseline_key]
                                baseline_metrics = scenario_metrics(
                                    baseline_raw,
                                    baseline_durations,
                                    item["costs"],
                                )
                            changed_improved_estimates = {
                                **changed_original,
                                **item["new_estimates"],
                            }
                            if changed_improved_estimates == improved_estimates:
                                improved_metrics = improved_control
                            else:
                                improved_raw = simulate_scenario(
                                    item["improved_bpmn"],
                                    log,
                                    log_activities,
                                    significant_durations,
                                    changed_improved_estimates,
                                    1.0,
                                )
                                improved_durations = build_duration_table(
                                    significant_durations,
                                    changed_improved_estimates,
                                    1.0,
                                    bpmn_preparation.prepare_bpmn(
                                        pm4py.read_bpmn(str(item["improved_bpmn"]))
                                    ),
                                )
                                improved_metrics = scenario_metrics(
                                    improved_raw,
                                    improved_durations,
                                    item["costs"],
                                )
                        else:
                            baseline_metrics = baseline_control
                            changed_new_estimates = scale_one_estimate(
                                item["new_estimates"],
                                activity,
                                factor,
                            )
                            changed_improved_estimates = {
                                **item["original_estimates"],
                                **changed_new_estimates,
                            }
                            if changed_improved_estimates == improved_estimates:
                                improved_metrics = improved_control
                            else:
                                improved_raw = simulate_scenario(
                                    item["improved_bpmn"],
                                    log,
                                    log_activities,
                                    significant_durations,
                                    changed_improved_estimates,
                                    1.0,
                                )
                                improved_durations = build_duration_table(
                                    significant_durations,
                                    changed_improved_estimates,
                                    1.0,
                                    bpmn_preparation.prepare_bpmn(
                                        pm4py.read_bpmn(str(item["improved_bpmn"]))
                                    ),
                                )
                                improved_metrics = scenario_metrics(
                                    improved_raw,
                                    improved_durations,
                                    item["costs"],
                                )

                        output_rows.append(
                            make_output_row(
                                item,
                                estimate_source,
                                activity,
                                estimate,
                                factor,
                                baseline_metrics,
                                improved_metrics,
                                baseline_control,
                                improved_control,
                            )
                        )

    elasticity_results = pd.DataFrame(output_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = (
        elasticity_results.groupby(
            ["Objective", "Perturbed estimate source", "Requested estimate factor"],
            dropna=False,
        )
        .mean(numeric_only=True)
        .reset_index()
    )
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        elasticity_results.to_excel(writer, index=False, sheet_name="results")
        summary.to_excel(writer, index=False, sheet_name="summary")
    csv_path = output_path.with_suffix(".csv")
    elasticity_results.to_csv(csv_path, index=False)
    print(
        f"Processed {len(results)} evaluation rows into "
        f"{len(elasticity_results)} individual-activity scenarios."
    )
    print(f"Excel results: {output_path}")
    print(f"CSV results:   {csv_path}")
    return elasticity_results


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, help="Evaluation results .xlsx workbook")
    parser.add_argument("--data-dir", type=Path, default=script_dir / "data")
    parser.add_argument("--config", type=Path, default=script_dir / "evaluation_config.json")
    parser.add_argument("--output", type=Path, help="Output .xlsx path")
    arguments = parser.parse_args()

    workbook_path = arguments.workbook or find_workbook(script_dir)
    workbook_path = workbook_path.resolve()
    output_path = arguments.output or workbook_path.parent / "activity_elasticity_results.xlsx"
    run(
        workbook_path,
        arguments.data_dir.resolve(),
        arguments.config.resolve(),
        output_path.resolve(),
    )
    return 0


if __name__ == "__main__":
    graphviz_bin = r"C:\Program Files\Graphviz\bin"
    if os.path.isdir(graphviz_bin) and graphviz_bin not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] += os.pathsep + graphviz_bin
    raise SystemExit(main())
