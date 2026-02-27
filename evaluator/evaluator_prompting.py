import importlib
import inspect
importlib.reload(inspect)

# prompt for estimating durations
def add_task_duration():
    return (
        "You are an expert in estimating the execution durations of activities in a business process. "
        "You are given two dictionaries with different activities from one process. "
        "The first dictionary contains activities and their known execution durations in hours. "
        "The second dictionary contains activities, but their execution durations are unknown. "
        "Your task is to estimate the execution durations of the activities in the second dictionary. "
        "Assume the role of the process owner and ensure that the proposed execution durations are plausible. "
        "Return ONLY a valid JSON object mapping each activity from the second dictionary to a numeric duration in hours. "
        "Use double quotes for all keys, provide numbers as plain numerals (no units), and do not include any extra commentary or code fences.\n\n"
    )
def add_dictionaries(dictionary_known, dictionary_unknown):
    return "Here is the first dictionary with known execution durations: \n" \
            + dictionary_known + "\n\n" \
            "Here is the second dictionary with unknown execution durations: \n" \
            + dictionary_unknown + "\n\n"

def add_prompt_duration(dictionary_known, dictionary_unknown):
    return add_task_duration() + add_dictionaries(dictionary_known, dictionary_unknown)
            