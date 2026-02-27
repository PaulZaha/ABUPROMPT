import pm4py
import pandas as pd
import numpy as np
import json
import re

from evaluator import evaluator_prompting, evaluator_requests

### functions to request missing durations from LLM
def check_for_unknown_durations(bpmn, sim_durations_df):

    unknown_durations = []

    # Make a list with the names of all unknown durations in significant_durations_df (activities that are in the bpmn but do not have a significant duration)
    bpmn_activities = [node.name for node in bpmn.get_nodes() if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Task)]

    for index, row in sim_durations_df.iterrows():
        if pd.isna(row["weighted_significant_duration"]):
            if row["activity"] in bpmn_activities:
                if row["activity"] not in unknown_durations:
                    unknown_durations.append(row["activity"])

    # check if all activities that are in the bpmn_graph are also in the weighted_significant_duration_df. If not, add them to the list of unknown durations
    for activity in bpmn_activities:
        if activity not in sim_durations_df["activity"].tolist():
            unknown_durations.append(activity)

    sim_durations_df = sim_durations_df.dropna()

    return unknown_durations, sim_durations_df

def request_missing_durations(unknown_durations, significant_durations_df, sim_durations_df):

    if len(unknown_durations) > 0:

        # prepare the known durations for the llm: make a dictionary with the activities as keys and the durations as values
        known_durations = {}
        for index, row in significant_durations_df.iterrows():
            if not pd.isna(row["weighted_significant_duration"]):
                known_durations[row["activity"]] = row["weighted_significant_duration"]

        # prepare a dict with NAs for the unknown durations
        unknown_durations = {activity: np.nan for activity in unknown_durations}

        # create a prompt for the LLM to estimate the unknown durations
        prompt = evaluator_prompting.add_prompt_duration(str(known_durations), str(unknown_durations))

        # status print
        print("Requesting unknown durations from LLM for the following activities:")
        print(unknown_durations)

        print("Sending the following known durations as a reference to the LLM:")
        print(known_durations)

        # request the unknown durations from the LLM
        response = evaluator_requests.OpenAI_Call_Durations(prompt)

        try:
            unknown_durations_estimates = json.loads(response)
        except json.JSONDecodeError:
            print(f"Failed to parse durations JSON: {response}")
            raise

        # status print
        print("Received the following estimated durations from LLM:")
        print(unknown_durations_estimates)

        print("Old sim_durations_df:")
        print(sim_durations_df)

        # add the newly estimated durations to sim_durations_df
        sim_durations_df = pd.concat([sim_durations_df, pd.DataFrame(unknown_durations_estimates.items(), columns=["activity", "weighted_significant_duration"])], ignore_index=True)

        print("Updated sim_durations_df:")
        print(sim_durations_df)

    else:
        unknown_durations_estimates = {}

    return sim_durations_df, unknown_durations_estimates

def get_sim_durations(bpmn, significant_durations_df, sim_durations_df):
    unknown_durations, sim_durations_df = check_for_unknown_durations(bpmn, sim_durations_df)
    sim_durations_df, unknown_durations_estimates = request_missing_durations(unknown_durations, significant_durations_df, sim_durations_df)
    return sim_durations_df, unknown_durations_estimates