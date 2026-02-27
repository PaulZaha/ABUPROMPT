import pm4py
import pandas as pd
from datetime import datetime

def evaluate_traces(bpmn, log):

    # convert bpmn to petri net
    net, im, fm = pm4py.convert_to_petri_net(bpmn)

    # Keep only log events that map to BPMN tasks when calculating durations
    bpmn_tasks = {
        node.name
        for node in bpmn.get_nodes()
        if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Task) and node.name
    }

    # Conformance checking via token-based replay (faster than alignments for fit detection)
    tbr_diagnostics_df = pm4py.conformance_diagnostics_token_based_replay(
        log,
        net,
        im,
        fm,
        activity_key='concept:name',
        case_id_key='case:concept:name',
        timestamp_key='time:timestamp',
        return_diagnostics_dataframe=True
    )

    # keep only traces that perfectly fit the model
    fit_case_ids = tbr_diagnostics_df.loc[tbr_diagnostics_df['is_fit'], 'case_id']

    # quick exit if nothing fits
    if fit_case_ids.empty:
        empty_df = pd.DataFrame(columns=['duration', 'trace', 'frequency'])
        return empty_df, empty_df.copy(), float('nan')

    filtered_log = log[log['case:concept:name'].isin(fit_case_ids)].copy()

    # collect unique fitting variants together with their statistics
    variant_records = []

    # take filtered log and split by variants
    for variant, subdf in pm4py.split_by_process_variant(filtered_log):
        # calculate the number of cases in the variant
        number_of_cases = len(subdf['case:concept:name'].unique())
        # get the duration of all individual cases in the variant (case:concept:name is the trace id)
        case_durations = []
        for case_id, case_df in subdf.groupby('case:concept:name'):
            # Consider only events that are part of the BPMN model
            case_events = case_df[case_df['concept:name'].isin(bpmn_tasks)]
            if case_events.empty:
                continue
            timestamps = case_events['time:timestamp']
            start_ts = timestamps.min()
            end_ts = timestamps.max()
            if isinstance(start_ts, datetime) and isinstance(end_ts, datetime) and end_ts >= start_ts:
                hours = (end_ts - start_ts).total_seconds() / 3600
                case_durations.append(hours)

        number_of_cases = len(case_durations)

        if number_of_cases == 0:
            mean_variant_duration_h = float('nan')
        else:
            mean_variant_duration_h = sum(case_durations) / number_of_cases
        variant_records.append({
            'trace': variant,
            'duration': mean_variant_duration_h,
            'frequency': number_of_cases
        })

    fitting_traces_df = pd.DataFrame(variant_records, columns=['duration', 'trace', 'frequency'])

    # make another df featuring the percentage of the traces
    fitting_traces_percentage_df = fitting_traces_df.copy()
    fitting_traces_percentage_df['percentage'] = (fitting_traces_percentage_df['frequency'] / fitting_traces_percentage_df['frequency'].sum()) * 100
    fitting_traces_percentage_df = fitting_traces_percentage_df.drop(columns=['frequency'])

    # prepare the df for the frontend
    fitting_traces_percentage_df["percentage"] = fitting_traces_percentage_df["percentage"].apply(lambda x: round(x, 2))
    fitting_traces_percentage_df["duration"] = fitting_traces_percentage_df["duration"].apply(lambda x: round(x, 2))
    fitting_traces_percentage_df.columns = ["Duration", "Trace", "Percentage"]
    fitting_traces_percentage_df = fitting_traces_percentage_df[["Duration", "Percentage", "Trace"]]
    fitting_traces_percentage_df = fitting_traces_percentage_df.sort_values(by='Percentage', ascending=False).reset_index(drop=True)

    # calculate the mean duration of all fitting traces (weighted by the frequency of the traces)
    mean_duration = (fitting_traces_df['duration'] * fitting_traces_df['frequency']).sum() / fitting_traces_df['frequency'].sum()
    print(mean_duration)

    return fitting_traces_df, fitting_traces_percentage_df, mean_duration
                