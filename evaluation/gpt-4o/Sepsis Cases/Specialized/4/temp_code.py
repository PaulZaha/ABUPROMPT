
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
validate_triage = gen.activity('Validate Triage Outcomes')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
treatment_confirmation = gen.activity('Treatment Confirmation')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

subprocess_0 = gen.xor(None, lacticacid) # lacticacid is optional, leucocytes and crp should not be; crp before lacticacid
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])
subprocess_1_confirm = gen.partial_order(dependencies = [(treatment_confirmation, subprocess_1)]) # Add confirmation step before treatments

subprocess_2 = gen.partial_order(dependencies = [(leucocytes, crp), (subprocess_0,)]) # crp and leucocytes are sequential before any lacticacid, lacticacid optional
subprocess_3 = gen.xor(None, subprocess_1_confirm)
subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_3)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, validate_triage), (validate_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)]) 
