
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

# Combine Leucocytes, CRP, and LacticAcid to be concurrent but mandatory following Sepsis Triage
subprocess_0 = gen.partial_order(dependencies = [(leucocytes,), (crp,), (lacticacid,)])

# Allow Medication procedure to be concurrent but mandatory following successful tests
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid,), (iv_antibiotics,)])

# Link the subprocess of tests directly into triage assessments, ensuring proper sequencing
subprocess_2 = gen.partial_order(dependencies = [(subprocess_0,), (subprocess_1,)])

# Final Model - Remove xor as it does not contribute to necessary treatment pathways
final_model = gen.partial_order(dependencies = [(er_registration, er_triage), 
                                                (er_triage, er_sepsis_triage), 
                                                (er_sepsis_triage, subprocess_2)]) 
