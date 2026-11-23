
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

# Updated activities incorporating improvement strategy
er_registration = gen.activity('ER Registration')
combined_triage = gen.activity('Combined Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid') # now mandatory
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Mandatory initial tests - consolidated
subprocess_initial_tests = gen.partial_order(dependencies = [(leucocytes,), (crp,), (lacticacid,)])

# Treatment path simplification
subprocess_treatment = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])

# Full process model after redesign
final_model = gen.partial_order(dependencies = [
    (er_registration, combined_triage), 
    (combined_triage, subprocess_initial_tests), 
    (subprocess_initial_tests, subprocess_treatment)
])
