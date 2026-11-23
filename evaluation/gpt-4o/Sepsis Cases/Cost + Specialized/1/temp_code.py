
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Introduced XOR for better decision structure in tests and treatments
subprocess_0 = gen.xor(leucocytes, gen.xor(crp, lacticacid))  # Decision-driven testing based on sepsis triage
subprocess_1 = gen.xor(iv_liquid, iv_antibiotics)  # Added XOR for streamlined treatments
subprocess_2 = gen.partial_order(dependencies = [(subprocess_0, subprocess_1)])  # Prioritize order post-test for treatment decisions

final_model = gen.partial_order(dependencies = [
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, subprocess_2)])  # Consolidated subprocesses for streamlined process flow, reducing costs and errors
