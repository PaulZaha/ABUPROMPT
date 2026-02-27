import pm4py
import numpy as np
import simpy
import pandas as pd
import pprint

from evaluator import sim_probabilities, sim_durations

# get new activities in the bpmn
def get_new_activities(bpmn, log_activities):
    new_activities = [node for node in bpmn.get_nodes() if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Activity) and node.name not in log_activities]
    return new_activities

# simulation with simpy
def simulate_process(env, bpmn_graph, gateway_arc_probabilities, new_activities, sim_durations_df):

    def handle_next_node(node, predecessor):

        if isinstance(node, pm4py.objects.bpmn.obj.BPMN.Task):
            return env.process(task(env, node, predecessor))
        
        elif isinstance(node, pm4py.objects.bpmn.obj.BPMN.ParallelGateway):
            return env.process(parallel_gateway(env, node, predecessor))

        elif isinstance(node, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway):
            return env.process(exclusive_gateway(node, predecessor))

        elif isinstance(node, pm4py.objects.bpmn.obj.BPMN.EndEvent):
            debug_log.append("End of process reached at " + str(env.now))
            # debugging: enable to see the debug log
            # pprint.pprint(debug_log)
            return env.timeout(0) # end of process reached

    def task(env, task, predecessor):
        # get the name of the task
        task_name = task.name
        # get the duration of the task
        task_duration = sim_durations_df[sim_durations_df["activity"] == task_name]["weighted_significant_duration"].values[0]

        debug_log.append("Task '" + task_name + "' started at " + str(env.now))
        yield env.timeout(task_duration)
        debug_log.append("Task '" + task_name + "' finished at " + str(env.now))

        # append the task to the visited events
        trace.append(task)

        # if task is a new activity, the predecessor remains the same
        if task in new_activities:
            predecessor = predecessor
        else:
            predecessor = task
            
        out_arc = task.get_out_arcs()[0]
        next_node = out_arc.get_target()

        proc = handle_next_node(next_node, predecessor)
        if proc: # only yield if there is a valid process
            yield proc

    def exclusive_gateway(gateway, predecessor):
        if gateway._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING:
                
            # increment the gateway encounter (encountering the gateway for the div_exclusive_encounter[gateway] time)
            div_exclusive_encounter[gateway] += 1

            # iterate through all diverging gateways that have encounter >= 1 and increment the gateways since the last encounter
            for div_gateway in diverging_exclusive_gateways:
                if div_exclusive_encounter[div_gateway] >= 1:
                    # append the list of gateways since the last encounter
                    div_exclusive_last[div_gateway]["gateways_since_last_encounter"].append(gateway)

            # get the gateways since last encounter for the current gateway
            gateways_since_last_encounter = div_exclusive_last[gateway]["gateways_since_last_encounter"]
            # reset the gateways since last encounter for the current gateway
            div_exclusive_last[gateway]["gateways_since_last_encounter"] = []

            # if the current encounter is in the probabilities, get the probabilities
            if div_exclusive_encounter[gateway] in gateway_arc_probabilities[gateway][predecessor]:
                # Get the probabilities of the arcs
                probabilities = gateway_arc_probabilities[gateway][predecessor][div_exclusive_encounter[gateway]]

            # if there are no probabilities for the current encounter, artificial probabilities are calculated to exit the loop as soon as possible
            else:
                debug_log.append("End of encounters for diverging gateway " + str(gateway.name))

                # get the last arc
                last_arc = div_exclusive_last[gateway]["last_arc"]

                # get the exclusive gateway that followed the last arc first
                gateway_following_last_arc = gateways_since_last_encounter[0]

                # check if last arc led into a simple loop --> check direction of the following gateway
                if gateway_following_last_arc._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING:
                    
                    # permanent exclusion: delete the key of the last taken arc from the div_exclusive_art_probabilities
                    debug_log.append("Permanent exclusion of arc leading to loop: " + str(last_arc))
                    div_exclusive_art_probabilities[gateway].pop(last_arc)
                    num_remaining_arcs = len(div_exclusive_art_probabilities[gateway])
                    debug_log.append("Number of remaining arcs: " + str(num_remaining_arcs))
                    probability_per_arc = 1/num_remaining_arcs
                    # set all probabilities in div_exclusive_art_probabilities to the probability per arc
                    for arc in div_exclusive_art_probabilities[gateway]:
                        div_exclusive_art_probabilities[gateway][arc] = probability_per_arc
                        
                elif len(div_exclusive_art_probabilities[gateway]) > 1:
                        
                    # temporary exclusion: if > 1 arc left, set the probability of the last taken arc temporarily to 0
                    debug_log.append("Temporary exclusion of arc leading to loop: " + str(last_arc))
                    div_exclusive_art_probabilities[gateway][last_arc] = 0
                    num_remaining_arcs = len(div_exclusive_art_probabilities[gateway]) - 1
                    debug_log.append("Number of remaining arcs: " + str(num_remaining_arcs))
                    probability_per_arc = 1/num_remaining_arcs
                    # set all probabilities in div_exclusive_art_probabilities to the probability per arc
                    for arc in div_exclusive_art_probabilities[gateway]:
                        if arc != last_arc:
                            div_exclusive_art_probabilities[gateway][arc] = probability_per_arc
           
                # Get the probabilities of the arcs
                probabilities = div_exclusive_art_probabilities[gateway]

            debug_log.append("Probabilities for gateway '" + str(gateway.name) + "' coming from predecessor '" + str(predecessor.name) + "' are: " + str(probabilities))

            # check if probabilities are all 0 (for marginal case: predecessor and successors in log, but no successor follows predecessor in the log)
            if all(prob == 0 for prob in probabilities.values()):
                # change the probabilities to 1/len(probabilities) for all arcs
                num_remaining_arcs = len(probabilities)
                probability_per_arc = 1/num_remaining_arcs
                for arc in probabilities:
                    probabilities[arc] = probability_per_arc
    
            # Based on the probabilities, choose the next node
            next_arc = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))

            # save the next arc as the last taken arc
            div_exclusive_last[gateway]["last_arc"] = next_arc

            next_node = next_arc.get_target()
            debug_log.append("Decided for branch that starts with: " + next_node.name)
            predecessor = predecessor # predecessor remains the same --> we did not encounter new activity yet, just indicated the direction to go
    
            proc = handle_next_node(next_node, predecessor)
            if proc: # only yield if there is a valid process
                yield proc
    
        # if it is a converging gateway, we only have one out arc and go to the next node. the current predecessor remains the same
        elif gateway._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING:

            # iterate through all diverging gateways that have encounter >= 1 and increment the gateways since the last encounter
            for div_gateway in diverging_exclusive_gateways:
                if div_exclusive_encounter[div_gateway] >= 1:
                    # append the list of gateways since the last encounter
                    div_exclusive_last[div_gateway]["gateways_since_last_encounter"].append(gateway)            

            next_arc = gateway.get_out_arcs()[0]
            next_node = next_arc.get_target()
            predecessor = predecessor # predecessor remains the same
            
            proc = handle_next_node(next_node, predecessor)
            if proc: # only yield if there is a valid process
                yield proc

    def parallel_gateway(env, gateway, predecessor):
        if gateway._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING:
            debug_log.append("Parallelity started")

            # define the starting nodes of the branches
            starting_arcs = gateway.get_out_arcs()
            starting_nodes = [arc.get_target() for arc in starting_arcs]
            predecessor = predecessor

            # Create all branch processes first and store them
            branch_processes = []
            for node in starting_nodes:
                proc = handle_next_node(node, predecessor)
                if proc:
                    branch_processes.append(proc)

            # if the gateway is a diverging and a converging gateway at the same time, we need to change the direction of the gateway back to converging (= default)
            if len(gateway.get_in_arcs()) > 1:
                gateway._Gateway__gateway_direction = pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING
                debug_log.append("Gateway " + str(gateway.name) + " changed to converging")
            
            # Yield all processes simultaneously
            yield env.all_of(branch_processes)

        elif gateway._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING:

            # access the counter of the converging gateway and deduct 1
            conv_parallel_counter[gateway] -= 1

            # check if the counter is 0
            if conv_parallel_counter[gateway] == 0:
                debug_log.append("Parallelity ended")

                # predecessor from the last task in the branch
                predecessor = predecessor

                # check if the current node is a normal converging parallel gateway
                if len(gateway.get_out_arcs()) == 1:
                    next_arc = gateway.get_out_arcs()[0]
                    next_node = next_arc.get_target()

                # check if parallel gateway is converging and diverging at the same time
                elif len(gateway.get_out_arcs()) > 1:
                    # change the type of the current gateway to diverging
                    gateway._Gateway__gateway_direction = pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING
                    debug_log.append("Gateway " + str(gateway.name) + " changed to diverging")
                    # next node is the current node
                    next_node = gateway

                proc = handle_next_node(next_node, predecessor)
                if proc:
                    yield proc
            
            else: # if the counter is not 0, do nothing
                yield env.timeout(0)
    
    # get the nodes of the bpmn graph
    nodes = bpmn_graph.get_nodes()

    # create a debug_log for the simulation
    debug_log = [] 

    # create a list for the trace of visited events
    trace = []
    
    # get the converging parallel gateways and make a dict with the number of incoming arcs
    converging_parallel_gateways = [node for node in nodes if isinstance(node, pm4py.objects.bpmn.obj.BPMN.ParallelGateway) and node._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING]

    conv_parallel_counter = {}
    for gateway in converging_parallel_gateways:
        in_arcs = gateway.get_in_arcs()
        in_arcs_count = len(in_arcs)
        conv_parallel_counter[gateway] = in_arcs_count

    # get the diverging exclusive gateways --> count them up (# encounters)
    diverging_exclusive_gateways = [node for node in nodes if isinstance(node, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway) and node._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING]
    
    # dict to count the encounters of the diverging exclusive gateways
    div_exclusive_encounter = {}
    for gateway in diverging_exclusive_gateways:
        div_exclusive_encounter[gateway] = 0

    # dict to save the last taken arc of the diverging exclusive gateways
    div_exclusive_last = {}
    for gateway in diverging_exclusive_gateways:
        div_exclusive_last[gateway] = {}
        div_exclusive_last[gateway]["last_arc"] = None
        div_exclusive_last[gateway]["gateways_since_last_encounter"] = []

    # dict for artificial probabilities after last encounter (initialized with 1)
    div_exclusive_art_probabilities = {}
    for gateway in diverging_exclusive_gateways:
        div_exclusive_art_probabilities[gateway] = {}
        for out_arc in gateway.get_out_arcs():
            div_exclusive_art_probabilities[gateway][out_arc] = 1

    # get the start node --> assumption: there is only one start node
    start_node = [node for node in nodes if isinstance(node, pm4py.objects.bpmn.obj.BPMN.StartEvent)][0]

    # get the first arc --> assumption: we have 1 arc going out of the start node
    start_node_arc = start_node.get_out_arcs()[0]
    # get the first node
    first_node = start_node_arc.get_target()
    # Define the current predecessor
    predecessor = start_node

    proc = handle_next_node(first_node, predecessor)

    if proc:
        yield proc

    # change all tasks in the trace to task.name
    trace = [task.name for task in trace]

    return trace

def run_simulation(bpmn, gateway_arc_probabilities, new_activities, sim_durations_df):
    # run the simulation 10000 times, save the results and calculate the mean
    results = []
    np.random.seed(42)
    for i in range(10000):
        env = simpy.Environment()
        trace = env.process(simulate_process(env, bpmn, gateway_arc_probabilities, new_activities, sim_durations_df))
        env.run()
        results.append({"duration": env.now, "trace": trace.value})
    results_df = pd.DataFrame(results)
    return results_df

def get_simulation_results(bpmn, log, log_activities, significant_durations_df, sim_durations_df):
    new_activities = get_new_activities(bpmn, log_activities)
    gateway_arc_probabilities = sim_probabilities.get_gateway_probabilities(bpmn, log, new_activities)
    sim_durations_df, unknown_durations_estimates = sim_durations.get_sim_durations(bpmn, significant_durations_df, sim_durations_df)
    results_df = run_simulation(bpmn, gateway_arc_probabilities, new_activities, sim_durations_df)

    # calculate adjusted duration of the process (adjusted duration = duration - duration of first event)
    results_df["Adj. Duration"] = np.nan
    for index, row in results_df.iterrows():
        first_event = row["trace"][0]
        first_event_duration = sim_durations_df[sim_durations_df["activity"] == first_event]["weighted_significant_duration"].values[0]
        # Avoid subtracting more than the simulated duration (loops can exaggerate the first activity duration)
        effective_first_duration = min(first_event_duration, row["duration"])
        adjusted_duration = row["duration"] - effective_first_duration
        results_df.at[index, "Adj. Duration"] = adjusted_duration

    # prepare results summary
    simulation_results_df = results_df.drop_duplicates(subset="duration").reset_index(drop=True)
    simulation_results_df['Percentage'] = (simulation_results_df['duration'].map(lambda x: len(results_df[results_df['duration'] == x]) / len(results_df))* 100)
    
    # prepare the df for the frontend
    simulation_results_df.columns = ["Duration", "Trace", "Adj. Duration", "Percentage"]
    simulation_results_df = simulation_results_df[["Duration", "Adj. Duration", "Percentage", "Trace"]]	
    simulation_results_df = simulation_results_df.sort_values(by='Percentage', ascending=False).reset_index(drop=True)

    # calculate the mean of durations in results_df
    mean_duration = np.mean(results_df["duration"])

    # calculate the mean of the adjusted durations
    adjusted_mean_duration = np.mean(results_df["Adj. Duration"])

    return simulation_results_df, mean_duration, adjusted_mean_duration, unknown_durations_estimates, sim_durations_df
