
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes_crp_combined = gen.activity('Leucocytes CRP Combined Test')
lacticacid = gen.activity('LacticAcid')
iv_liquid_antibiotics_combined = gen.activity('IV Liquid & Antibiotics Combined')

subprocess_2 = gen.partial_order(dependencies = [(leucocytes_crp_combined,), (lacticacid,)])
subprocess_3 = gen.partial_order(dependencies = [(iv_liquid_antibiotics_combined,)])
subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_3)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)])