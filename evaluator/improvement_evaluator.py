from evaluator import evaluator_traces, evaluator_simulation

# evaluate the old process
def evaluate_old_process(input_bpmn, log, log_activities, significant_durations_df, sim_durations_df):
    
    # evaluate old model
    # old model traces results
    print("Trace evaluation old model")
    fitting_traces_df, fitting_traces_percentage_df, mean_duration_traces = evaluator_traces.evaluate_traces(input_bpmn, log)
    print("Mean traces duration old model: ", mean_duration_traces)

    # old model simulation results
    print("Simulation evaluation old model")
    simulation_results_df, mean_duration_simulation, adjusted_mean_duration, unknown_durations_estimates, sim_durations_df = evaluator_simulation.get_simulation_results(input_bpmn, log, log_activities, significant_durations_df, sim_durations_df)
    print("Mean duration simulation old model: ", mean_duration_simulation)
    print("Adjusted mean duration old model: ", adjusted_mean_duration)

    # get the accurracy of the simulation
    simulation_accuracy = abs(adjusted_mean_duration - mean_duration_traces) / mean_duration_traces
    print(f"Simulation deviation [%]: {simulation_accuracy}")

    return fitting_traces_percentage_df, mean_duration_traces, simulation_results_df, mean_duration_simulation, adjusted_mean_duration, unknown_durations_estimates, sim_durations_df

def evaluate_new_process(improved_bpmn, log, log_activities, significant_durations_df, sim_durations_df, mean_duration_simulation):

    # evaluate new model
    print("Simulation evaluation new model")
    new_simulation_results_df, new_mean_duration, new_adjusted_mean_duration, new_unknown_durations_estimates, sim_durations_df = evaluator_simulation.get_simulation_results(improved_bpmn, log, log_activities, significant_durations_df, sim_durations_df)
    print("Mean duration simulation new model: ", new_mean_duration)
    print("Adjusted mean duration new model: ", new_adjusted_mean_duration)

    # get the time saved by the improvement --> compare with simulation
    time_saved_percentage = (mean_duration_simulation - new_mean_duration) / mean_duration_simulation
    print(f"Time saved by the improvement [%]: {time_saved_percentage}")

    return new_simulation_results_df, new_mean_duration, new_adjusted_mean_duration, new_unknown_durations_estimates, time_saved_percentage