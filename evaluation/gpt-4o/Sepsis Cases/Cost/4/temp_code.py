
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

# Simplification by removing optional elements that don't have clear necessity initially
# Consider triage results to determine necessity of tests
subprocess_tests = gen.xor(lacticacid, None)  # Only perform lactic acid test if indicated by triage
subprocess_2 = gen.partial_order(dependencies = [(leucocytes, crp)])
subprocess_treatments = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])

# Subordinate tests and treatments under triage decision after sepsis triage
subprocess_4 = gen.xor(subprocess_2, subprocess_tests)  # Tests are conditional upon necessity post-triage
subprocess_5 = gen.xor(subprocess_4, subprocess_treatments) # Treatments only if necessary post-tests

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)])
