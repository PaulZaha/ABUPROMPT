import pm4py
from pm4py.objects.process_tree.obj import ProcessTree

# start creating string with the powl code

def get_process_tree_from_bpmn(bpmn):
    process_tree = pm4py.convert_to_process_tree(bpmn)
    return process_tree

def initiate_code():
    return "from generator.model_generator import ModelGenerator \n\n" \
            "gen = ModelGenerator()\n\n"

def initiate_activities(process_tree):
    def extract_activities(process_tree):
        activities = []
        if process_tree.label:
            activities.append(process_tree.label)
        for child in process_tree.children:
            activities.extend(extract_activities(child))
        return activities
    activities = extract_activities(process_tree)
    activity_code = ""
    for activity in activities:
        activity_code += f"{activity.lower().replace(' ', '_').replace('(', '').replace(')', '')} = gen.activity('{activity}')\n"

    return activity_code

def initiate_subprocesses(process_tree):
    
    x = 0
    mapping = {}

    def replace_subprocesses(process_tree):

        # function to check if a node is a leaf node; true if node has no children
        def is_leaf(node):
            return len(node.children) == 0 

        # function to check if a node has only leaf children; true if all children are leaf nodes
        def has_only_leaf_children(node):
            return all(is_leaf(child) for child in node.children)

        # get the type of a node: X, +, ->
        def get_node_type(node):
            return node.operator if hasattr(node, "operator") else None

        # get the children of a node that have only leaf children and replace them with a new node
        def get_children_with_only_leaf_children(process_tree):
            nonlocal x
            for i, child in enumerate(process_tree.children):
                if is_leaf(child):
                    continue
                elif has_only_leaf_children(child):
                    new_node_label = "subprocess_" + str(x)
                    process_tree.children[i] = pm4py.objects.process_tree.obj.ProcessTree(label=new_node_label)
                    mapping[new_node_label] = [get_node_type(child), child.children]
                    x += 1
                else:
                    get_children_with_only_leaf_children(child)
            return process_tree
        
        # recursively replace subprocesses with new nodes until all subprocesses are replaced
        while not all(is_leaf(child) for child in process_tree.children):
            get_children_with_only_leaf_children(process_tree)
        
        return process_tree
    
    new_process_tree = replace_subprocesses(process_tree)

    # create code for subprocesses
    code = "\n"
    for key, value in mapping.items():
        # print(f"For {key}, subprocess type is X")  # Debug print	
        tasks = [task.label for task in value[1]]
        # print(f"Tasks for key {key}: {tasks}")  # Debug print
        tasks = [task.lower().replace(" ", "_").replace('(', '').replace(')', '') if task is not None else "None" for task in tasks] # replace None with "None" string
        #print(f"Processing key: {key}, value0: {value[0]}, value1: {value[1]}")  # Debug print
        if str(value[0]) == "X":
            code += f"{key} = gen.xor({', '.join(tasks)})\n" 
        elif str(value[0]) == "+":
            code += f"{key} = gen.partial_order(dependencies = [{', '.join(f'({task},)' for task in tasks)}])\n"
        elif str(value[0]) == "->":
            dependencies = ", ".join([f"({tasks[i]}, {tasks[i+1]})" for i in range(len(tasks)-1)])
            code += f"{key} = gen.partial_order(dependencies = [{dependencies}])\n"
        elif str(value[0]) == "*":
            code += f"{key} = gen.loop({tasks[0]}, {tasks[1]})\n"
    return code, new_process_tree

def create_final_model(process_tree):
    dependencies = ", ".join([f"({process_tree.children[i].label.lower().replace(" ", "_").replace('(', '').replace(')', '')}, {process_tree.children[i+1].label.lower().replace(" ", "_").replace('(', '').replace(')', '')})" for i in range(len(process_tree.children)-1)])
    code = f"\nfinal_model = gen.partial_order(dependencies = [{dependencies}])"
    return code

def create_powl_code(bpmn):
    process_tree = get_process_tree_from_bpmn(bpmn)
    # this is needed because process_tree will be modified
    process_tree_original = get_process_tree_from_bpmn(bpmn)
    initiate_subprocesses_code, new_process_tree = initiate_subprocesses(process_tree)
    code = initiate_code() + initiate_activities(process_tree_original) + initiate_subprocesses_code + create_final_model(new_process_tree)
    return code