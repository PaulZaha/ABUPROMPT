
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Removing optional check of 'lacticacid', assuming it's redundant in the context
subprocess_1 = gen.partial_order(dependencies=[(iv_liquid, iv_antibiotics)])

# Making Leucocytes and CRP tests concurrent to reduce time
subprocess_2 = gen.partial_order(dependencies=[(leucocytes,), (crp,)])

# Streamlining optional parallel subprocess flows by removal
subprocess_4 = gen.partial_order(dependencies=[(subprocess_2, subprocess_1)])

final_model = gen.partial_order(dependencies=[(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_4)])
