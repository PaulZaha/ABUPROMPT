
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

subprocess_0 = gen.xor(None, lacticacid)

# Improve parallel execution by allowing Leucocytes, CRP, and LacticAcid concurrently with IV Liquid and IV Antibiotics
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid,), (iv_antibiotics,)])
subprocess_2 = gen.partial_order(dependencies = [(leucocytes,), (crp,), (subprocess_0,)])

# Combine subprocesses to directly allow parallel execution, avoiding unnecessary XOR
concurrent_activities = gen.partial_order(dependencies = [(subprocess_2,), (subprocess_1,)])

# Final Model combining optimized concurrency
final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, concurrent_activities)])
