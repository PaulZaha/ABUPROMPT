
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
review_results = gen.activity('Review Lab Results')
confirm_diagnosis = gen.activity('Confirm Diagnosis before Treatment')

subprocess_0 = gen.partial_order(dependencies=[(leucocytes, crp, lacticacid)])
subprocess_1 = gen.partial_order(dependencies = [(subprocess_0, review_results), (review_results, confirm_diagnosis)])
subprocess_2 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])
subprocess_3 = gen.xor(None, subprocess_2)
subprocess_4 = gen.partial_order(dependencies = [(subprocess_1, subprocess_3)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)])
