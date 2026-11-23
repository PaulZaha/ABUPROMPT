
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
sepsis_risk_assessment = gen.activity("Sepsis Risk Assessment")
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')
treatment_confirmation = gen.activity('Treatment Confirmation')

test_choice_submodel = gen.xor(leucocytes, crp, lacticacid) 

subprocess_0 = gen.partial_order(dependencies = [( test_choice_submodel,)])
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])
subprocess_1_with_confirmation = gen.partial_order(dependencies = [(treatment_confirmation, subprocess_1)])
subprocess_3 = gen.xor(None, subprocess_1_with_confirmation)
subprocess_4 = gen.partial_order(dependencies = [(subprocess_0, subprocess_3)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, sepsis_risk_assessment), (sepsis_risk_assessment, er_sepsis_triage), (er_sepsis_triage, subprocess_5)]) 
