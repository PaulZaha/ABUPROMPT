import numpy as np
import json
import pm4py

from evaluator.cost import cost_prompting, cost_requests


def get_defined_costs():
    defined_costs = {
    'Create Fine': 15.0,
    'Send Fine': 10.0,
    'Insert Fine Notification': 5.0,
    'Add penalty': 10.0,
    'Payment': 3.0,
    'Send for Credit Collection': 25.0,
    'Insert Date Appeal to Prefecture': 3.0,
    'Send Appeal to Prefecture': 8.0,
    'Receive Result Appeal from Prefecture': 8.0,
    'Notify Result Appeal to Offender': 5.0,
    'Appeal to Judge': 50.0
    }
    return defined_costs

def get_unknown_costs(bpmn, defined_costs):

    bpmn_activities = (node.name for node in bpmn.get_nodes() if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Activity))

    # find unknown costs and make a dict with them
    unknown_costs = {}
    for activity in bpmn_activities:
        if activity not in defined_costs:
            unknown_costs[activity] = np.nan

    return unknown_costs

def request_unknown_costs(unknown_costs, defined_costs):
    if len(unknown_costs)>0:
        prompt = cost_prompting.add_prompt_cost(
            json.dumps(defined_costs),
            json.dumps({activity: None for activity in unknown_costs}),
        )

        # status print
        print("Requesting unknown execution cost from LLM for the following activities:")
        print(unknown_costs)

        print("Sending the following known execution cost as a reference to the LLM:")
        print(defined_costs)

        # request the unknown durations from the LLM
        try:
            unknown_costs_estimates = json.loads(cost_requests.OpenAI_Call_Costs(prompt))
        except json.JSONDecodeError:
            print("Failed to parse cost estimates from model response.")
            raise

        # status print
        print("Received the following estimated costs from LLM:")
        print(unknown_costs_estimates)

        print("Old defined_costs:")
        print(defined_costs)

        # update estimated costs df with unknown costs estimates (append new key value pairs)
        for key, value in unknown_costs_estimates.items():
            try:
                defined_costs[key] = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid cost value returned for activity '{key}': {value}") from exc

        print("Updated defined_costs:")
        print(defined_costs)

    else:
        unknown_costs_estimates = {}

    return defined_costs, unknown_costs_estimates

def evaluate_costs(defined_costs, results_df):

    # add new cost column
    results_df["Cost"] = np.nan

    # sort the columns
    if "Adj. Duration" in results_df.columns:
        results_df = results_df[["Duration", "Adj. Duration", "Cost", "Percentage", "Trace"]]
    else:
        results_df = results_df[["Duration", "Cost", "Percentage", "Trace"]]

    for index, row in results_df.iterrows():
        results_df.at[index, "Cost"] = sum([defined_costs[activity] for activity in row["Trace"]])

    # calculate the mean costs of the traces
    mean_costs = sum(results_df["Cost"] * (results_df["Percentage"] / 100))
        
    return results_df, mean_costs

