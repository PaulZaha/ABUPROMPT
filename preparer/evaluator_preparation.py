import os
import pandas as pd
import pm4py
import numpy as np

### general preparation for the evaluation

def load_vars_paths_durs(vars_paths_durs_path, log):
    # check if the file exists first
    if not os.path.exists(vars_paths_durs_path):
        # get the dataframe with the variables, paths and durations
        dataframe = pm4py.format_dataframe(log)
        vars_paths_durs = pm4py.get_variants_paths_duration(dataframe)
        vars_paths_durs.to_csv(vars_paths_durs_path, index=False)

    # load existing file
    vars_paths_durs = pd.read_csv(vars_paths_durs_path, sep=',')
    return vars_paths_durs


def load_unique_combinations(unique_combinations_path, vars_paths_durs):
    # get all unique combinations of activities and their global mean durations -> calculate using the variants_paths_duration
    # check if the file exists first
    if not os.path.exists(unique_combinations_path):

        # make a df with every unique combination of concept:name and concept_name_2
        unique_combinations = vars_paths_durs[['concept:name', 'concept:name_2']].drop_duplicates()

        # for every unique combination in unique_combinations: iterate through all of them in df and multiply the value in the column '@@flow_time' with the value in the column '@@variant_count'
        for index, row in unique_combinations.iterrows():
            weight = 0
            acc_time = 0
            # get the concept:name and concept_name_2
            concept_name = row['concept:name']
            concept_name_2 = row['concept:name_2']
            # get the indices where the concept:name and concept_name_2 are equal to the current concept_name and concept_name_2
            indices = vars_paths_durs.index[(vars_paths_durs['concept:name'] == concept_name) & (vars_paths_durs['concept:name_2'] == concept_name_2)].tolist()
            # multiply the value in the column '@@flow_time' with the value in the column '@@variant_count' for every index in indices
            for i in indices:
                acc_time_position_current_case = vars_paths_durs.at[i, '@@flow_time'] * vars_paths_durs.at[i, '@@variant_count']
                acc_time = acc_time + acc_time_position_current_case
                weight = weight + vars_paths_durs.at[i, '@@variant_count']
            mean_time_position_over_all_cases = acc_time / weight
            unique_combinations.at[index, 'mean_time_position_over_all_cases'] = mean_time_position_over_all_cases
            unique_combinations.at[index, 'frequency'] = weight

        # save unique combinations to a csv file
        unique_combinations.to_csv(unique_combinations_path, index=False)

    # load existing file
    unique_combinations = pd.read_csv(unique_combinations_path, sep=',')
    return unique_combinations
    
    
def get_log_statistics(log, vars_paths_durs_path, unique_combinations_path):
    vars_paths_durs = load_vars_paths_durs(vars_paths_durs_path, log)
    unique_combinations = load_unique_combinations(unique_combinations_path, vars_paths_durs)
    return vars_paths_durs, unique_combinations
    

### preparation for the simulation

def create_durations_matrix(log_activities, unique_combinations):
    # get durations from unique_combinations and put them in a matrix, thereby row from durations_matrix = source, column from durations_matrix = target
    durations_matrix = pd.DataFrame(columns=log_activities, index=log_activities)
    for index, row in unique_combinations.iterrows():
        source = row["concept:name"]
        target = row["concept:name_2"]
        duration = row["mean_time_position_over_all_cases"]
        durations_matrix.at[source, target] = duration
    return durations_matrix


def create_frequency_matrix(log_activities, unique_combinations):
    frequency_matrix = pd.DataFrame(columns=log_activities, index=log_activities)
    for index, row in unique_combinations.iterrows():
        source = row["concept:name"]
        target = row["concept:name_2"]
        frequency = row["frequency"]
        frequency_matrix.at[source, target] = frequency
    # fill NaN values with 0 (NaN = no occurrences)
    frequency_matrix = frequency_matrix.fillna(0)
    return frequency_matrix


def create_significance_matrix(log_activities, frequency_matrix, output_path):
    # calculate the significance of every sequence flow using their frequency
    significance_matrix = pd.DataFrame(columns=log_activities, index=log_activities)

    for index, row in frequency_matrix.iterrows(): # index is row name, row is row data
        for column in frequency_matrix.columns:
            if not index == column:
                # calculate the significance for different activities in source and target
                frequency_source_target = abs(frequency_matrix.at[index, column])
                frequency_target_source = abs(frequency_matrix.at[column, index])
                significance = (frequency_source_target - frequency_target_source) / ((frequency_source_target + frequency_target_source) + 1)
                significance_matrix.at[index, column] = significance
            elif index == column:
                # calculate the significance for the same activity in source and target
                frequency_source_source = abs(frequency_matrix.at[index, column])
                significance = frequency_source_source/(frequency_source_source + 1)
                significance_matrix.at[index, column] = significance  
    # save the significance matrix as a csv file in the temp folder
    significance_matrix_path = os.path.join(output_path, "significance_matrix.csv")
    significance_matrix.to_csv(significance_matrix_path, index=False)
    return significance_matrix


def create_significant_durations_df(significance_matrix, durations_matrix, frequency_matrix):

    # set the threshold for significance
    threshold = 0.7

    # Calculate the weighted significant duration for each activity using the sequence flows with a significance above the threshold
    weighted_significant_duration_df = pd.DataFrame(columns=["activity", "weighted_significant_duration"])

    for index, column in enumerate(significance_matrix.columns):
        # get the targets of all significant sequence flows (smaller than -0.7 or bigger than 0.7) for which a duration exists
        significant_sequence_flows = significance_matrix[column][(significance_matrix[column].abs() > threshold) & durations_matrix[column].notna()]
        # if there are significant sequence flows, calculate the weighted significant duration
        if not significant_sequence_flows.empty:
            numerator = sum([durations_matrix.at[row, column]*frequency_matrix.at[row, column] for row in significant_sequence_flows.index])
        # if there are no significant sequence flows, the weighted significant duration is NaN --> therefore the weighted significant duration is NaN
        else:
            numerator = np.nan

        denominator = frequency_matrix[column].sum()
        if denominator == 0:
            weighted_significant_duration = np.nan
        else:
            weighted_significant_duration = numerator/denominator

        weighted_significant_duration_df = pd.concat([weighted_significant_duration_df, pd.DataFrame({"activity": column, "weighted_significant_duration": weighted_significant_duration}, index=[0])], ignore_index=True)

        weighted_significant_duration_df_h = weighted_significant_duration_df.copy()
        weighted_significant_duration_df_h["weighted_significant_duration"] = (
            pd.to_numeric(
                weighted_significant_duration_df_h["weighted_significant_duration"],
                errors="coerce",
            ) / 3600
        ).round(2)

    return weighted_significant_duration_df_h


def get_significant_durations_matrix(log_activities, unique_combinations, output_path):
    durations_matrix = create_durations_matrix(log_activities, unique_combinations)
    frequency_matrix = create_frequency_matrix(log_activities, unique_combinations)
    significance_matrix = create_significance_matrix(log_activities, frequency_matrix, output_path)
    significant_durations_matrix = create_significant_durations_df(significance_matrix, durations_matrix, frequency_matrix)
    return significant_durations_matrix

# main function to prepare the evaluation
def prepare_evaluation(log, vars_paths_durs_path, unique_combinations_path, log_activities, output_path):
    vars_path_durs, unique_combinations = get_log_statistics(log, vars_paths_durs_path, unique_combinations_path)
    significant_durations_matrix = get_significant_durations_matrix(log_activities, unique_combinations, output_path)
    return vars_path_durs, unique_combinations, significant_durations_matrix

def prepare_log(log_path, output_path):

    # paths to files needed for the evaluation --> they will be saved in the same directory as the log file
    log_name = os.path.splitext(os.path.basename(log_path))[0] # name of the bpmn input file (before the file extension)
    # define path for vars_paths_durs file --> same directory as the log file
    vars_paths_durs_path = os.path.join(os.path.dirname(log_path), f'{log_name}_vars_paths_durs.csv')
    # define path for unique_combinations file --> same directory as the log file
    unique_combinations_path = os.path.join(os.path.dirname(log_path), f'{log_name}_unique_combinations.csv')

    # read the log and get the activities
    log = pm4py.read_xes(log_path)
    log_activities = pm4py.get_event_attribute_values(log, "concept:name")

    # get data needed for evaluation
    vars_path_durs, unique_combinations, significant_durations_df = prepare_evaluation(log, vars_paths_durs_path, unique_combinations_path, log_activities, output_path)

    return log, log_activities, vars_path_durs, unique_combinations, significant_durations_df
