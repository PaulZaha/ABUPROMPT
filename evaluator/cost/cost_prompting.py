import importlib
import inspect
importlib.reload(inspect)

# prompt for estimating durations
def add_task_cost():
    return (
        "You are an expert in estimating the execution costs of activities in a business process. "
        "You are given two dictionaries with different activities from one process. "
        "The first dictionary contains activities and their known execution costs. "
        "The second dictionary contains activities, but their execution costs are unknown. "
        "Your task is to estimate the execution costs of the activities in the second dictionary. "
        "Assume the role of the process owner and utilize your expertise about the process context to ensure that the proposed execution costs are plausible. "
        "Return ONLY a valid JSON object that maps each activity from the second dictionary to a numeric cost. "
        "Use double quotes for all keys and do not include any additional commentary or code fences."
    )
def add_dictionaries(dictionary_known, dictionary_unknown):
    return (
        "Here is the first dictionary with known execution cost: \n"
        + dictionary_known
        + "\n\n"
        + "Here is the second dictionary with unknown execution cost: \n"
        + dictionary_unknown
        + "\n\n"
    )

def add_prompt_cost(dictionary_known, dictionary_unknown):
    return add_task_cost() + add_dictionaries(dictionary_known, dictionary_unknown)
            
            