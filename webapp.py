# to run ABUPROMPT in Browser:
# streamlit run ABUPROMPT.py

import streamlit as st
import pm4py
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
import os
import pandas as pd
from datetime import datetime
import tempfile
import shutil
import uuid

from generator import improvement_generator
from evaluator import improvement_evaluator
from evaluator.cost import cost_evaluator
from preparer import bpmn_preparation, evaluator_preparation


graphviz_bin = r"C:\Program Files\Graphviz\bin"

if os.path.isdir(graphviz_bin) and graphviz_bin not in os.environ.get("PATH", "").split(os.pathsep):
    os.environ["PATH"] += os.pathsep + graphviz_bin

# set page config
st.set_page_config(layout="wide")

# set title and description
st.markdown("## ABUPROMPT: Automated Business Process Optimizer")

# initialize indicator variables
new_mean_duration = None
improved_bpmn = None
mean_duration_simulation = None
log = None

unknown_costs = None
unknown_costs_estimates = None

input_bpmn_filename = "input"
output_bpmn_filename = "improved"
output_path_prefix = "runs/"
os.makedirs(output_path_prefix, exist_ok=True)

# initialize a per-session temp directory for early previews (avoid creating run dirs prematurely)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "session_temp_dir" not in st.session_state:
    st.session_state.session_temp_dir = os.path.join(tempfile.gettempdir(), f"ABUPROMPT_{st.session_state.session_id}")
    os.makedirs(st.session_state.session_temp_dir, exist_ok=True)
if "input_bpmn_path" not in st.session_state:
    st.session_state.input_bpmn_path = None
if "input_png_path" not in st.session_state:
    st.session_state.input_png_path = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "output_path" not in st.session_state:
    st.session_state.output_path = None

with st.sidebar:
    st.markdown("### Input Data")

    file = st.file_uploader("Upload BPMN file", type=["bpmn"])

    # Only process new uploads; store in a per-session temp dir so we can preview immediately
    if file is not None and st.session_state.uploaded_file_name != file.name:
        # reset any previously computed state tied to an old upload
        st.session_state.uploaded_file_name = file.name

        temp_bpmn_path = os.path.join(st.session_state.session_temp_dir, input_bpmn_filename + ".bpmn")
        with open(temp_bpmn_path, "wb") as input_file:
            input_file.write(file.getbuffer())

        input_bpmn = pm4py.read_bpmn(temp_bpmn_path)
        input_bpmn = bpmn_preparation.prepare_bpmn(input_bpmn)
        pm4py.write_bpmn(input_bpmn, temp_bpmn_path)

        # save the visualization of the input bpmn to session temp dir
        parameters = bpmn_visualizer.Variants.CLASSIC.value.Parameters
        visualization = bpmn_visualizer.apply(input_bpmn, parameters={parameters.FORMAT: 'png'})
        temp_png_path = os.path.join(st.session_state.session_temp_dir, input_bpmn_filename + ".png")
        bpmn_visualizer.save(visualization, temp_png_path)

        # remember paths for later display and for copying into the run dir when Start is clicked
        st.session_state.input_bpmn_path = temp_bpmn_path
        st.session_state.input_png_path = temp_png_path

    event_log_path = st.text_input("Enter XES log file path")

    if event_log_path:
        # if log path starts and ands with ", remove them
        if event_log_path.startswith('"') and event_log_path.endswith('"'):
            event_log_path = event_log_path[1:-1]
        
    # improvement goal selection
    standard_goal = st.selectbox("Choose standard optimization goal", ("", "Time", "Cost"))
    if standard_goal == "Time":
        standard_goal = "reduce process execution time"
    elif standard_goal == "Cost":
        standard_goal = "reduce process execution cost"
    custom_goal = st.text_input("Enter custom optimization goal")

    # button to start the process improvement
    start = st.button("Start", type="primary", help="Start the process improvement.")

    # error and status information
    if start:
        # check if all required inputs are provided
        if st.session_state.input_bpmn_path and ((standard_goal or custom_goal) or (standard_goal and custom_goal)) and event_log_path:

            # create the run-specific output directory once at start
            if not st.session_state.output_path:
                st.session_state.output_path = os.path.join(output_path_prefix, datetime.now().strftime("%Y%m%d_%H%M%S"))
                os.makedirs(st.session_state.output_path, exist_ok=True)

                # copy prepared input BPMN and preview PNG into the run directory
                shutil.copy(st.session_state.input_bpmn_path, os.path.join(st.session_state.output_path, input_bpmn_filename + ".bpmn"))
                if st.session_state.input_png_path and os.path.exists(st.session_state.input_png_path):
                    shutil.copy(st.session_state.input_png_path, os.path.join(st.session_state.output_path, input_bpmn_filename + ".png"))

            with st.spinner(text="Reading log file...", show_time=True):
                # prepare or retrieve the cached log --> those variables are stored in the session state (RAM): no need to recompute them
                if "log" not in st.session_state:
                    (
                        st.session_state.log,
                        st.session_state.log_activities,
                        st.session_state.vars_path_durs,
                        st.session_state.unique_combinations,
                        st.session_state.significant_durations_df
                    ) = evaluator_preparation.prepare_log(event_log_path, st.session_state.output_path)
                    
                log = st.session_state.log
                log_activities = st.session_state.log_activities
                vars_path_durs = st.session_state.vars_path_durs
                unique_combinations = st.session_state.unique_combinations
                significant_durations_df = st.session_state.significant_durations_df

            # extract the log name from the event_log_path --> if it is the road traffic fine management process, cost information is available
            log_name = os.path.basename(event_log_path)
            cost_information = False
            if log_name == "Road_Traffic_Fine_Management_Process.xes":
                cost_information = True

            # load the prepared input BPMN from the run dir
            input_bpmn = pm4py.read_bpmn(os.path.join(st.session_state.output_path, input_bpmn_filename + ".bpmn"))

            # check if the activities in the bpmn are all in the log
            if not all(activity in log_activities for activity in [node.name for node in input_bpmn.get_nodes() if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Task)]):
                st.error("BPMN tasks not in the log. Please start new session.")
                st.stop()

            else:

                with st.spinner(text="Improving Process...", show_time=True):

                    # choose the goal based on standard or custom input
                    if standard_goal and not custom_goal:
                        goal = standard_goal
                    elif custom_goal and not standard_goal:
                        goal = custom_goal
                    elif standard_goal and custom_goal:
                    # concatenate both goals to one string
                        goal = standard_goal + " and " + custom_goal
                    explanation, improved_bpmn = improvement_generator.improve_process(input_bpmn, goal, st.session_state.output_path)
                    # persist improvement info for display after reruns
                    st.session_state.improved_bpmn = True
                    st.session_state.explanation = explanation

                    # evaluation of old process --> significant durations als sim durations df übergeben
                    if "fitting_traces_percentage_df" not in st.session_state:
                        (
                            st.session_state.fitting_traces_percentage_df,
                            st.session_state.mean_duration_traces,
                            st.session_state.simulation_results_df,
                            st.session_state.mean_duration_simulation,
                            st.session_state.adjusted_mean_duration,
                            st.session_state.unknown_durations_estimates,
                            st.session_state.sim_durations_df
                        ) = improvement_evaluator.evaluate_old_process(input_bpmn, log, log_activities, significant_durations_df, significant_durations_df)

                    fitting_traces_percentage_df = st.session_state.fitting_traces_percentage_df
                    mean_duration_traces = st.session_state.mean_duration_traces
                    simulation_results_df = st.session_state.simulation_results_df
                    mean_duration_simulation = st.session_state.mean_duration_simulation
                    adjusted_mean_duration = st.session_state.adjusted_mean_duration
                    unknown_durations_estimates = st.session_state.unknown_durations_estimates
                    sim_durations_df = st.session_state.sim_durations_df
                    
                    # evaluation of new process
                    new_simulation_results_df, new_mean_duration, new_adjusted_mean_duration, new_unknown_durations_estimates, time_saved_percentage = improvement_evaluator.evaluate_new_process(improved_bpmn, log, log_activities, significant_durations_df, sim_durations_df, mean_duration_simulation)
                    st.session_state.new_simulation_results_df = new_simulation_results_df
                    st.session_state.new_mean_duration = new_mean_duration
                    st.session_state.new_adjusted_mean_duration = new_adjusted_mean_duration
                    st.session_state.new_unknown_durations_estimates = new_unknown_durations_estimates
                    st.session_state.time_saved_percentage = time_saved_percentage

                    # if cost information is available: also evaluate costs
                    if cost_information:
                        defined_costs = cost_evaluator.get_defined_costs()
                        unknown_costs = cost_evaluator.get_unknown_costs(improved_bpmn, defined_costs)
                        if unknown_costs:
                            defined_costs, unknown_costs_estimates = cost_evaluator.request_unknown_costs(unknown_costs, defined_costs)
                        fitting_traces_percentage_df, mean_cost_traces = cost_evaluator.evaluate_costs(defined_costs, fitting_traces_percentage_df)
                        simulation_results_df, mean_cost_simulation = cost_evaluator.evaluate_costs(defined_costs, simulation_results_df)
                        new_simulation_results_df, new_mean_cost = cost_evaluator.evaluate_costs(defined_costs, new_simulation_results_df)
                        st.session_state.new_simulation_results_df = new_simulation_results_df
                        st.session_state.new_mean_cost = new_mean_cost
                        st.session_state.unknown_costs_estimates = unknown_costs_estimates

                st.success("Process improved!")

        elif not st.session_state.input_bpmn_path:
            st.error("Please upload a BPMN file.")
        elif not event_log_path:
            st.error("Please enter the path to the log file.")
        elif not (standard_goal or custom_goal):
            st.error("Please choose a standard optimization goal or enter a custom optimization goal.")
        elif (standard_goal and custom_goal):
            st.error("Please choose either a standard optimization goal or enter a custom optimization goal, not both.")

    # button to clear the session state and start a new session
    new_session = st.button("New Session", type="secondary", help="Click this to start a new session.")
    if new_session:
        # try to clean up the temp dir for this session
        try:
            if os.path.isdir(st.session_state.get("session_temp_dir", "")):
                shutil.rmtree(st.session_state.session_temp_dir, ignore_errors=True)
        except Exception:
            pass
        st.session_state.clear()
            
# visualize process models
if st.session_state.get("input_png_path") and os.path.exists(st.session_state.input_png_path):
    st.image(st.session_state.input_png_path, caption="Original Process Model")
elif st.session_state.get("output_path") and os.path.exists(os.path.join(st.session_state.output_path, input_bpmn_filename + ".png")):
    st.image(os.path.join(st.session_state.output_path, input_bpmn_filename + ".png"), caption="Original Process Model")

if st.session_state.get("improved_bpmn"):
    st.image(os.path.join(st.session_state.output_path, output_bpmn_filename + ".png"), caption="Improved Process Model")

    with open(os.path.join(st.session_state.output_path, output_bpmn_filename + ".bpmn"), "rb") as file:
        new_bpmn_file = file.read()

    st.download_button(
        label="Download improved BPMN",
        data=new_bpmn_file,
        file_name=output_bpmn_filename + ".bpmn",
        mime="text/plain",
        icon = ":material/download:"
    )

    with st.expander("Improvement Explanation", icon=":material/question_mark:", expanded=False):
        st.write(st.session_state.get("explanation", ""))

# summary of the evaluation results
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:

    if mean_duration_simulation is not None:

        st.markdown("##### Ground Truth Original Model")
        st.button(f"True duration [h]: {round(mean_duration_traces, 2)}", type="tertiary", help="Duration based on the true distribution and duration of traces.", key = "old_true_duration", icon = ":material/info:")
        
        if cost_information:
            st.button(f" ", type="tertiary", key = "spacing_1")
            st.button(f" ", type="tertiary", key = "spacing_2")
            st.button(f"True cost [€]: {round(mean_cost_traces, 2)}", type="tertiary", help="Cost based on the true distribution of traces.", key = "old_true_cost", icon = ":material/info:")

with col2:

    if mean_duration_simulation is not None:

        st.markdown("##### Approximation Original Model")

        st.button(f"Adjusted duration [h]: {round(adjusted_mean_duration, 2)}", type="tertiary", help="Duration estimated based on simulation, deducted first activity's duration.", key = "old_adjusted_duration", icon = ":material/info:")
        st.button(f"Estimated duration [h]: {round(mean_duration_simulation, 2)}", type="tertiary", help="Duration estimated based on simulation.", key = "old_estimated_duration", icon = ":material/info:")
        st.button(f"Simulation deviance [%]: {round((abs(adjusted_mean_duration - mean_duration_traces) / mean_duration_traces)*100, 2)}", type="tertiary", help="Deviance of the estimated duration from the true duration.", key = "simulation_deviance", icon = ":material/info:")

        if cost_information:
            st.button(f"Estimated cost [€]: {round(mean_cost_simulation, 2)}", type="tertiary", help="Cost estimated based on simulation.", key = "old_estimated_cost", icon = ":material/info:")
            st.button(f"Cost deviance [%]: {round((abs(mean_cost_simulation - mean_cost_traces) / mean_cost_traces)*100, 2)}", type="tertiary", help="Deviance of the estimated cost from the true cost.", key = "cost_deviance", icon = ":material/info:")

with col3:
    
    if new_mean_duration is not None:

        st.markdown("##### Approximation New Model")
        st.button(f"Adjusted duration [h]: {round(new_adjusted_mean_duration, 2)}", type="tertiary", help="Duration estimated based on simulation, deducted first activity's duration.", key = "new_adjusted_duration", icon = ":material/info:")
        st.button(f"Estimated duration [h]: {round(new_mean_duration,2)}", type="tertiary", help="Duration estimated based on simulation.", key = "new_estimated_duration", icon = ":material/info:")

        if time_saved_percentage > 0:
            st.button(f"Process time decrease [%]: {round((abs(time_saved_percentage)*100),2)}", type="tertiary", help="Process time decrease by the improvement.", key = "time_decrease", icon = ":material/info:")
        else:
            st.button(f"Process time increase [%]: {round((abs(time_saved_percentage)*100),2)}", type="tertiary", help="Process time increase by the improvement.", key = "time_increase", icon = ":material/info:")
        
        if cost_information:
            st.button(f"Estimated cost [€]: {round(new_mean_cost, 2)}", type="tertiary", help="Cost estimated based on simulation.", key = "new_estimated_cost", icon = ":material/info:")

            cost_saved_percentage = (mean_cost_simulation - new_mean_cost) / mean_cost_simulation
            if cost_saved_percentage > 0:
                st.button(f"Process cost decrease [%]: {round((abs(cost_saved_percentage)*100),2)}", type="tertiary", help="Process cost decrease by the improvement.", key = "cost_decrease", icon = ":material/info:")
            else:
                st.button(f"Process cost increase [%]: {round((abs(cost_saved_percentage)*100),2)}", type="tertiary", help="Process cost increase by the improvement.", key = "cost_increase", icon = ":material/info:")
        
with col4:

    if mean_duration_simulation is not None:

        st.markdown("##### Activity Estimations by LLM")

        # show estimates on old model (= estimates on unsignificant activities)
        if unknown_durations_estimates: 
            st.button(f"Estimated activities in original model: ", type="tertiary", help="Activity durations estimated by LLM.", key = "LLM_estimates_1", icon = ":material/info:")
            # put unknown_durations_estimates in a df
            unknown_durations_estimates_df = pd.DataFrame(unknown_durations_estimates.items(), columns=["Activity", "Duration"])
            st.dataframe(unknown_durations_estimates_df, hide_index=True)
        else:
            st.button(f"No estimated activities in original model.", type="tertiary", help="All information retrievable from the log: No activity durations are estimated by LLM.", key = "LLM_no_estimates", icon = ":material/info:")

    if new_mean_duration is not None:

        # show new estimates
        if new_unknown_durations_estimates:
            # put new_unknown_durations_estimates in a df
            new_unknown_durations_estimates_df = pd.DataFrame(new_unknown_durations_estimates.items(), columns=["Activity", "Duration"])
            
            if unknown_costs_estimates:
                st.button(f"Estimated activities in new model: ", type="tertiary", help="Activity durations and costs estimated by LLM.", key = "LLM_estimates_2", icon = ":material/info:")
                new_estimates_df = new_unknown_durations_estimates_df.merge(pd.DataFrame(unknown_costs_estimates.items(), columns=["Activity", "Cost"]), on="Activity")
                st.dataframe(new_estimates_df, hide_index=True)
            else:
                st.button(f"Estimated activities in new model: ", type="tertiary", help="Activity durations estimated by LLM.", key = "LLM_estimates_3", icon = ":material/info:")
                st.dataframe(new_unknown_durations_estimates_df, hide_index=True)
        else:
            if cost_information:
                st.button(f"No estimated activities in new model.", type="tertiary", help="All information retrievable from the log: No activity durations or costs estimated by LLM.", key = "LLM_estimates_4", icon = ":material/info:")
            else:
                st.button(f"No estimated activities in new model.", type="tertiary", help="No activity durations estimated by LLM.", key = "LLM_no_estimates_2", icon = ":material/info:")

tab1, tab2 = st.tabs(["Traces Original Model", "Traces New Model"])

with tab1:
    if mean_duration_simulation is not None:

        col5, col6 = st.columns([1, 1])

        with col5:
            # display df from trace evaluation
            st.button(f"Original Model's True Trace Distribution:", type="tertiary", help="Trace distribution based on conformance checking.", key = "old_true_trace_distribution", icon = ":material/info:")
            st.dataframe(fitting_traces_percentage_df)

        # dfs with trace distributions
        with col6:
            # display df from simulation evaluation
            st.button(f"Original Model's Approximated Trace Distribution:", type="tertiary", help="Trace distribution based on simulation.", key = "old_estimated_trace_distribution", icon = ":material/info:")
            st.dataframe(simulation_results_df)

with tab2:
    if new_mean_duration is not None:

        col7, col8 = st.columns([1, 1])

        with col7:

            # display df from simulation evaluation
            st.button(f"Original Model's Approximated Trace Distribution:", type="tertiary", help="Trace distribution based on simulation.", key = "old_estimated_trace_distribution_2", icon = ":material/info:")
            st.dataframe(simulation_results_df)
            
        with col8:

            # display df with traces from simulation
            st.button(f"New Model's Approximated Trace Distribution:", type="tertiary", help="Trace distribution based on simulation.", key = "new_estimated_trace_distribution", icon = ":material/info:")
            st.dataframe(new_simulation_results_df)            

