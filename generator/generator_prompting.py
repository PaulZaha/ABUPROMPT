import importlib
import inspect
importlib.reload(inspect)


def add_task(improvement_goal: str) -> str:
    return (
        "You are an expert in business process improvement and business process redesign. "
        "You are given a business process in POWL code and the following improvement goal(s) for the process: "
        + improvement_goal
        + ". "
        "Analyze the process, identify process elements that can be improved, and propose improvements specifically targeted at achieving the given improvement goal(s). "
        "Assume the role of the process owner and utilize your expertise about the process context to ensure that the proposed improvements are feasible. "
        "Return ONLY a valid JSON object that contains two keys: 'explanation' and 'code'. "
        "The value for 'explanation' should provide a description of your improvements and explain how they contribute to achieving the improvement goal(s). "
        "The value for 'code' should contain the updated POWL code as a string, formatted as valid Python code."
    )


def add_powl_knowledge() -> str:
    return "Use the following knowledge about the POWL process modeling language:\n" \
            "A POWL model is a hierarchical model, recursively generated" \
            " by combining submodels into a new model either using an operator (xor or loop)" \
            " or as a partial order. \n\n " \
            " Three types of POWL models: \n"\
            " 1. base case consisting of a single activity \n"\
            " 2. uses an operator (xor or loop) to combine" \
            " multiple POWL models into a new model: xor to model an exclusive choice" \
            " of n >= 2 sub-models; loop to model a do-redo loop of 2 POWL models \n" \
            " 3. partial order over n >= 2 submodels: partial order is binary relation that is irreflexive, transitive," \
            " and asymmetry. \n\n" \
            "ModelGenerator provides the functions described below:\n" \
            " - activity(str:activity_label) generates an activity. \n" \
            " - xor(*args) takes n >= 2 arguments, which are the submodels. Use it to model exclusive choice" \
            " structures between paths, e.g. xor(path_1, path_2). You can also use xor(submodel, None) to make a submodel optional; " \
            "i.e., to model an exclusive choice between executing this submodel or skipping it.\n" \
            " - loop(do, redo) takes 2 arguments. Use it to model cyclic" \
            " behavior; i.e., the do part is executed once first, and every time the redo part is executed, it" \
            " is followed by another execution of the do part. You" \
            " can also use loop to model a self-loop by setting the redo part to None; i.e., to indicate that the do part" \
            " can be repeated from 1 to n. You can also model a skippable self-loop by" \
            " setting the do part to None instead; i.e., to indicate that the redo part can be repeated from 0 to" \
            " n. You can use a self-loop to model that in a complicated process you can go back" \
            " to certain initial stage: first you model the complicated process, then you put it inside a loop.\n" \
            " - partial_order(dependencies) takes 1 argument, a list of tuples of submodels. These tuples" \
            " set the nodes of the partial order and specify the edges of the partial order (i.e., the sequential dependencies)." \
            " The transitive closure of the added dependencies should conform with the irreflexivity" \
            " requirement of partial orders. We interpret unconnected nodes in a partial order to be" \
            " concurrent and connections between nodes as sequential dependencies. Use a partial order" \
            " with no edges (with the parameter 'dependencies' set to a list of tuples of size 1) to model pure" \
            " concurrency/independency. The general assumption is partial orders is that nodes are concurrent; however, you can" \
            " still add sequential dependencies between certain nodes (as tuples in the list for the parameter" \
            " 'dependencies'). Assume we have 4 submodel A, B, C, D. partial_order(dependencies=[(A, B), (B, C), (C, D)]) " \
            "models a sequence A -> B -> C -> D; partial_order(dependencies=[(A,), (B,), (C,), (D,)]) models full" \
            " concurrency; partial_order(dependencies=[(A,B), (C,), (D,)]) models" \
            " concurrency with the sequential dependency A -> B. Avoid using a partial order as a child of" \
            " another partial order to ensure not leaving out any sequential dependencies. To resolve this, you can combine the two orders.\n" \
            "Note: for any powl model, you can always call powl.copy() to create another instance" \
            " of the same model. This is useful to model cases where a subporcess or activity can be executed exactly" \
            "twice (not really in a loop). \n\n"


def add_output_requirements() -> str:
    return (
        "Follow these output requirements: "
        "Return only valid Python code that leverages the ModelGenerator API to define the improved process model. "
        "Use exactly one import statement: 'from generator.model_generator import ModelGenerator'. "
        "Assign the resulting process model to a variable named 'final_model'. "
    )


def add_original_model(powl_code: str) -> str:
    original_model = "```python\n" + str(powl_code) + "```\n"
    return "Here is the POWL model to improve:\n" + original_model


def add_prompt(improvement_goal: str, powl_code: str) -> tuple[str, str]:
    system_prompt = add_task(improvement_goal) + add_powl_knowledge() + add_output_requirements()
    user_prompt = add_original_model(powl_code)
    return system_prompt, user_prompt
            