import os
import json
import pm4py
from pm4py.objects.conversion.powl.converter import apply as powl_to_pn
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer

from generator import generator_requests, generator_prompting
from preparer import bpmn_preparation, bpmn_to_powl


def create_prompts(goal, input_bpmn):
    # convert the input BPMN to a POWL code
    input_powl_code = bpmn_to_powl.create_powl_code(input_bpmn)
    # generate separated system and user prompts
    return generator_prompting.add_prompt(goal, input_powl_code)


def persist_outputs(code, explanation, output_path):
    code_clean = (code or "").strip()
    explanation_clean = (explanation or "").strip()

    if not code_clean:
        raise ValueError("LLM response did not contain improved POWL code.")

    code_path = os.path.join(output_path, "improved_model_code.py")
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code_clean)

    explanation_path = os.path.join(output_path, "improvement_explanation.txt")
    with open(explanation_path, 'w', encoding='utf-8') as f:
        f.write(explanation_clean)

    return code_clean, explanation_clean


def check_code(code):

    code_valid = False

    # check if import statement in code is correct: only 1 import statement allowed, called "from generator import ModelGenerator"
    if code.count('import') > 1:
        raise Exception('Only one import statement is allowed in the code.')
    elif code.count('from generator.model_generator import ModelGenerator') != 1:
        raise Exception('The import statement is missing or incorrect.')

    # check if system functions (os.remove(), os.rmdir(), shutil.rmtree()) or eval exec is used in the code
    if 'os.remove(' in code or 'os.rmdir(' in code or 'shutil.rmtree(' in code or 'eval(' in code or 'exec(' in code:
        raise Exception('The code contains a forbidden function.')

    # check if the code contains "final_model"
    if 'final_model' not in code:
        raise Exception('The code does not contain the final model.')
    
    code_valid = True

    return code_valid


def execute_code(code, output_path):
    # execute the code
    context = {}
    exec(code, context)

    final_model = context["final_model"]

    # get petri net, convert it to BPMN and visualize it
    net, im, fm = powl_to_pn(final_model)
    improved_bpmn = pm4py.convert.convert_to_bpmn(net, im, fm)

    # prepare the new bpmn (add gateway directions)
    improved_bpmn = bpmn_preparation.prepare_bpmn(improved_bpmn)

    improved_bpmn_path = os.path.join(output_path, "improved.bpmn")
    pm4py.write_bpmn(improved_bpmn, improved_bpmn_path)
    new_png_path = os.path.join(output_path, "improved.png")
    parameters = bpmn_visualizer.Variants.CLASSIC.value.Parameters
    visualization = bpmn_visualizer.apply(improved_bpmn, parameters={parameters.FORMAT: 'png'})
    bpmn_visualizer.save(visualization, new_png_path)

    return improved_bpmn


def improve_process(input_bpmn, goal, output_path):

    system_prompt, user_prompt = create_prompts(goal, input_bpmn)

    response_raw = generator_requests.OpenAI_Call_Improvement(system_prompt, user_prompt)

    try:
        response_json = json.loads(response_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response for improvement is not valid JSON") from exc

    code = response_json.get("code")
    explanation = response_json.get("explanation")

    code, explanation = persist_outputs(code, explanation, output_path)

    check_code(code)

    improved_bpmn = execute_code(code, output_path)

    return explanation, improved_bpmn
