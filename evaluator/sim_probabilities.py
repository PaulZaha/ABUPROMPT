import pm4py

### functions to get gateway probabilities

def get_diverging_exclusive_gateways(bpmn):
    exclusive_gateways = [node for node in bpmn.get_nodes() if isinstance(node, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway)]
    diverging_exclusive_gateways = [gateway for gateway in exclusive_gateways if gateway._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING]
    return diverging_exclusive_gateways

# get predecessors of a gateway
def get_predecessors(gateway, new_activities):

    def follow_up_predecessors(node, visited=None, parallel_gateway_opened=False):
        
        if visited is None:
            visited = set()
            
        predecessors = []
        if node in visited:
            return predecessors
        
        visited.add(node)
        in_arcs = node.get_in_arcs()
        
        for arc in in_arcs:
            source = arc.get_source()

            if isinstance(source, pm4py.objects.bpmn.obj.BPMN.Activity):
                # if source is a new activity, continue the search
                if source in new_activities:
                    predecessors.extend(follow_up_predecessors(source, visited))
                # if source is not a new activity, add it to the predecessors
                else:
                    predecessors.append(source)

            elif isinstance(source, pm4py.objects.bpmn.obj.BPMN.StartEvent):
                predecessors.append(source)

            elif isinstance(source, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway):
                if parallel_gateway_opened:
                    predecessors.extend(follow_up_predecessors(source, visited, parallel_gateway_opened))
                else:
                    predecessors.extend(follow_up_predecessors(source, visited))

            elif isinstance(source, pm4py.objects.bpmn.obj.BPMN.ParallelGateway):
                # check if it is converging or diverging
                if source._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING:
                    parallel_gateway_opened = True # When we see a converging gateway while going backwards, we set the flag
                    predecessors.extend(follow_up_predecessors(source, visited, parallel_gateway_opened))
                elif source._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING:
                    if parallel_gateway_opened:
                        # If we see a diverging gateway and we previously saw its converging pair, we stop the search in this direction
                        return predecessors
                    else:
                        # If we haven't seen a converging gateway, continue the search
                        predecessors.extend(follow_up_predecessors(source, visited))
        return predecessors

    predecessors = follow_up_predecessors(gateway)
    return predecessors

def get_predecessors_all_gateways(diverging_exclusive_gateways, new_activities):
    # # find all predecessors of the gateways
    gateway_predecessors = {}
    for gateway in diverging_exclusive_gateways:
        gateway_predecessors[gateway] = get_predecessors(gateway, new_activities)
    return gateway_predecessors


# get task successors of individual gateways
def get_successors(gateway, new_activities):

    def follow_up_successors(node, visited=None, parallel_gateway_opened=False):

        if visited is None:
            visited = set()
            
        successors = []
        if node in visited:
            return successors
        
        visited.add(node)
        out_arcs = node.get_out_arcs()
        
        for arc in out_arcs:
            target = arc.get_target()

            if isinstance(target, pm4py.objects.bpmn.obj.BPMN.Activity):
                # check if target is a new activity
                if target in new_activities:
                    successors.extend(follow_up_successors(target, visited))
                else:
                    successors.append(target)

            elif isinstance(target, pm4py.objects.bpmn.obj.BPMN.EndEvent):
                successors.append(target)

            elif isinstance(target, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway):
                if parallel_gateway_opened:
                    successors.extend(follow_up_successors(target, visited, parallel_gateway_opened))
                else:	
                    successors.extend(follow_up_successors(target, visited))

            elif isinstance(target, pm4py.objects.bpmn.obj.BPMN.ParallelGateway):
                if target._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING:
                    parallel_gateway_opened = True
                    successors.extend(follow_up_successors(target, visited, parallel_gateway_opened))
                elif target._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING:
                    if parallel_gateway_opened:
                        return successors
                    else:
                        successors.extend(follow_up_successors(target, visited))

        return successors

    gateway_out_arcs = gateway.get_out_arcs()
    gateway_arc_successors = {}

    visited = set()

    for arc in gateway_out_arcs:
        parallel_gateway_opened = False
        target = arc.get_target()
        
        if isinstance(target, pm4py.objects.bpmn.obj.BPMN.Activity):
            # check if target is a new activity
            if target in new_activities:
                gateway_arc_successors[arc] = follow_up_successors(target, visited)
            else:
                gateway_arc_successors[arc] = [target]

        elif isinstance(target, pm4py.objects.bpmn.obj.BPMN.EndEvent):
            gateway_arc_successors[arc] = [target]

        elif isinstance(target, pm4py.objects.bpmn.obj.BPMN.ExclusiveGateway):
            if parallel_gateway_opened == True:
                gateway_arc_successors[arc] = follow_up_successors(target, visited, parallel_gateway_opened)
            else:	
                gateway_arc_successors[arc] = follow_up_successors(target, visited)

        elif isinstance(target, pm4py.objects.bpmn.obj.BPMN.ParallelGateway):
            if target._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.DIVERGING:
                parallel_gateway_opened = True
                gateway_arc_successors[arc] = follow_up_successors(target, visited, parallel_gateway_opened)
            elif target._Gateway__gateway_direction == pm4py.objects.bpmn.obj.BPMN.Gateway.Direction.CONVERGING:
                if parallel_gateway_opened:
                    return gateway_arc_successors
                else:
                    gateway_arc_successors[arc] = follow_up_successors(target, visited)

    return gateway_arc_successors

def get_successors_all_gateways(diverging_exclusive_gateways, new_activities):
    gateway_arc_successors = {}
    for gateway in diverging_exclusive_gateways:
        gateway_arc_successors[gateway] = get_successors(gateway, new_activities)
    return gateway_arc_successors

# allocate frequencies to the successors of the gateways depending on the predecessors
def prepare_successor_counting(log, diverging_exclusive_gateways, gateway_arc_successors, gateway_predecessors):

    # get start events
    start_events = pm4py.get_start_activities(log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp') # returns dict with key = start event, value = count

    # map successors directly to gateways (needed for frequency allocation)
    gateway_successors = {}
    for gateway in diverging_exclusive_gateways:
        gateway_successors[gateway] = []
        for arc in gateway_arc_successors[gateway]:
            for successor in gateway_arc_successors[gateway][arc]:
                gateway_successors[gateway].append(successor)

    # initalize nested dict for the predecessor dependent frequencies of the successors (needed for frequency allocation)
    gateway_path_frequencies = {}
    for gateway in diverging_exclusive_gateways:
        gateway_path_frequencies[gateway] = {}
        for predecessor in gateway_predecessors[gateway]: 
            gateway_path_frequencies[gateway][predecessor] = {}
            for successor in gateway_successors[gateway]:
                gateway_path_frequencies[gateway][predecessor]= {}
    
    return start_events, gateway_path_frequencies, gateway_successors


def filter_log_count_successors(log, predecessor, successors, gateway_path_frequencies, start_events, gateway):

    def check_suffix(suffix_variant, suffix_variant_frequency, predecessor, task_successors, end_successor, gateway_encounter):

        # initialize dict frequencies for current gateway encounter and every successor
        if gateway_encounter not in gateway_path_frequencies[gateway][predecessor]:
                gateway_path_frequencies[gateway][predecessor][gateway_encounter] = {}
        for successor in task_successors:
            if successor not in gateway_path_frequencies[gateway][predecessor][gateway_encounter]:
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][successor] = 0
        if end_successor:
            if end_successor not in gateway_path_frequencies[gateway][predecessor][gateway_encounter]:
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][end_successor] = 0

        # check if trace only consists of the predecessor --> then we attribute the frequency to the end event
        if len(suffix_variant) == 1 and suffix_variant[0] == predecessor.name:
            if end_successor:
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][end_successor] += suffix_variant_frequency

        else:
            # remove the predecessor from the suffix
            suffix_variant = suffix_variant[1:]

            # initialize variable to check if any task successor is in the suffix variant
            successors_in_suffix = [task_successor for task_successor in task_successors if task_successor.name in suffix_variant]

            if successors_in_suffix:

                # find the indices of all successors that are activities in the suffix and check which one comes first
                successors_in_suffix_index = {}
                for successor in successors_in_suffix:
                    successors_in_suffix_index[successor] = suffix_variant.index(successor.name)

                # get the successor that comes first in the suffix
                first_successor = min(successors_in_suffix_index, key=successors_in_suffix_index.get)

                # increment the frequency of the successor that comes first by the frequency of the suffix variant
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][first_successor] += suffix_variant_frequency

                # cut the suffix right after the occurrence of the first successor (take suffix but do not keep first successor, because of simple loops)
                cutted_suffix_variant_successor = suffix_variant[suffix_variant.index(first_successor.name)+1:]
                
                # check if further checks on suffix variant are needed: check if the predecessor is again in the suffix
                if predecessor.name in cutted_suffix_variant_successor:
                    # cut the suffix variant right before the first occurrence of the predecessor --> trace a b c d e c d and predecessor is c --> keep cdecd
                    cutted_suffix_variant = cutted_suffix_variant_successor[cutted_suffix_variant_successor.index(predecessor.name):]
                    # initiate the recursive function with the cutted suffix variant
                    gateway_encounter += 1
                    check_suffix(cutted_suffix_variant, suffix_variant_frequency, predecessor, task_successors, end_successor, gateway_encounter)

            if not successors_in_suffix and end_successor and len(suffix_variant) > 0:
                # if no other successor is in the trace, increment the frequency of the end event by the frequency of the suffix variant
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][end_successor] += suffix_variant_frequency

    # initialize the gateway encounter
    gateway_encounter = 1

    # make a list to identify the kind of successor
    task_successors = []
    end_successor = None
    for successor in successors:
        if isinstance(successor, pm4py.objects.bpmn.obj.BPMN.EndEvent):
            end_successor = successor
        else:
            task_successors.append(successor)

    # common case: predecessor is a task
    if isinstance(predecessor, pm4py.objects.bpmn.obj.BPMN.Task):

        # from the log, keep only the suffixes of predecessor (strict = False --> keeps the predecessor in the suffix)
        filtered_log_suffixes = pm4py.filter_suffixes(log, predecessor.name, strict=False)
        # get the variants of the filtered log suffixes --> dict with key = variant, value = count
        suffix_variants = pm4py.get_variants(filtered_log_suffixes)

        # iterate through all suffix variants and check the suffixes for the eventually follows relations of the successors with the predecessor
        for suffix_variant in suffix_variants:
            suffix_variant_frequency = suffix_variants[suffix_variant]
            check_suffix(suffix_variant, suffix_variant_frequency, predecessor, task_successors, end_successor, gateway_encounter)

    # exeptional case: predecessor is a start event
    # frequency allocation if predecessor = start event can happen outside of the function because this always happens only once & we do not need to check suffixes but the whole variants of the log
    elif isinstance(predecessor, pm4py.objects.bpmn.obj.BPMN.StartEvent):

        # initialize dict frequencies for gateway encounter and every successor
        if gateway_encounter not in gateway_path_frequencies[gateway][predecessor]:
                gateway_path_frequencies[gateway][predecessor][gateway_encounter] = {}
        for successor in successors:
            if successor not in gateway_path_frequencies[gateway][predecessor][gateway_encounter]:
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][successor] = 0
        
        # get the process variants of the complete log and count frequencies of task successors in every variant
        process_variants = pm4py.get_variants(log)
        for variant in process_variants:
            # get the frequency of the variant
            variant_frequency = process_variants[variant]
            # initialize variable to check if any task successor is in the suffix variant
            successors_in_variant = [task_successor for task_successor in task_successors if task_successor.name in variant] # we do not count successors that are end events in this case, because: frequency of path start -> end is always 0, because process never happened

            if successors_in_variant:
                # find the indices of all successors that are activities in the trace and check which one comes first
                successors_in_variant_index = {}
                for successor in successors_in_variant:
                    successors_in_variant_index[successor] = variant.index(successor.name)
                # get the successor that comes first in the trace
                first_successor = min(successors_in_variant_index, key=successors_in_variant_index.get)
                # increment the frequency of the successor that comes first by the frequency of the variant
                gateway_path_frequencies[gateway][predecessor][gateway_encounter][first_successor] += variant_frequency

    return gateway_path_frequencies

def get_gateway_successor_frequencies(diverging_exclusive_gateways, log, gateway_predecessors, gateway_successors, start_events, gateway_path_frequencies):

    for gateway in diverging_exclusive_gateways:
    
        predecessors = gateway_predecessors[gateway]
        successors = gateway_successors[gateway]

        for predecessor in predecessors:
            # we check the suffixes for all eventually follows relations of the successors with the predecessor
            # special handling: successor = end event --> for current encounter: we count traces where no other successor is in the trace (& no next encounter happens, but this is implicitly the case, as a next encounter can only happen if there is a task-successor in the trace)
            gateway_path_frequencies = filter_log_count_successors(log, predecessor, successors, gateway_path_frequencies, start_events, gateway)

    return gateway_path_frequencies

def calculate_probabilities(diverging_exclusive_gateways, gateway_path_frequencies, gateway_predecessors, gateway_successors):
    # take the gateway_path_frequencies and make another dict gateway_probabilities from it
    gateway_probabilities = {}
    for gateway in diverging_exclusive_gateways:
        gateway_probabilities[gateway] = {}
        for predecessor in gateway_predecessors[gateway]:
            gateway_probabilities[gateway][predecessor] = {}
            for encounter in gateway_path_frequencies[gateway][predecessor]:
                gateway_probabilities[gateway][predecessor][encounter] = {}
                cumulated_frequency_successors = sum(gateway_path_frequencies[gateway][predecessor][encounter].values())
                for successor in gateway_successors[gateway]:
                    if cumulated_frequency_successors == 0:
                        probability = 0
                    else:
                        probability = gateway_path_frequencies[gateway][predecessor][encounter][successor]/cumulated_frequency_successors
                    gateway_probabilities[gateway][predecessor][encounter][successor] = probability
    return gateway_probabilities

def map_probabilities_to_arcs(gateway_probabilities, gateway_arc_successors, gateway_predecessors):
    # map the gateway probabilities to the gateway arcs
    gateway_arc_probabilities = {}
    for gateway in gateway_arc_successors:
        gateway_arc_probabilities[gateway] = {}
        for predecessor in gateway_predecessors[gateway]:
            gateway_arc_probabilities[gateway][predecessor] = {}
            for encounter in gateway_probabilities[gateway][predecessor]:
                gateway_arc_probabilities[gateway][predecessor][encounter] = {}
                for arc in gateway_arc_successors[gateway]:
                    gateway_arc_probabilities[gateway][predecessor][encounter][arc] = 0
                    for successor in gateway_arc_successors[gateway][arc]:
                        if successor in gateway_probabilities[gateway][predecessor][encounter]:
                            gateway_arc_probabilities[gateway][predecessor][encounter][arc] += gateway_probabilities[gateway][predecessor][encounter][successor]
    return gateway_arc_probabilities


def get_gateway_probabilities(bpmn, log, new_activities):
    diverging_exclusive_gateways = get_diverging_exclusive_gateways(bpmn)
    gateway_predecessors = get_predecessors_all_gateways(diverging_exclusive_gateways, new_activities)
    gateway_arc_successors = get_successors_all_gateways(diverging_exclusive_gateways, new_activities)
    start_events, gateway_path_frequencies, gateway_successors = prepare_successor_counting(log, diverging_exclusive_gateways, gateway_arc_successors, gateway_predecessors)
    gateway_path_frequencies = get_gateway_successor_frequencies(diverging_exclusive_gateways, log, gateway_predecessors, gateway_successors, start_events, gateway_path_frequencies)
    gateway_probabilities = calculate_probabilities(diverging_exclusive_gateways, gateway_path_frequencies, gateway_predecessors, gateway_successors)
    gateway_arc_probabilities = map_probabilities_to_arcs(gateway_probabilities, gateway_arc_successors, gateway_predecessors)
    return gateway_arc_probabilities