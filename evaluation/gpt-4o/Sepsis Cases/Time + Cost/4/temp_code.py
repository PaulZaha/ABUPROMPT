
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

# Improved parallelization of diagnostic tests (leucocytes, CRP, optional lactic acid)
subprocess_0 = gen.xor(None, lacticacid)
subprocess_2 = gen.partial_order(dependencies=[(leucocytes,), (crp,), (subprocess_0,)])

# Enhanced treatment administration: IV Liquid and IV Antibiotics concurrently (if feasible)
subprocess_1 = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])

# Reimagined subprocess 3 and 4 to encourage concurrency after sepsis triage when feasible
subprocess_4 = gen.partial_order(dependencies=[(subprocess_2,), (subprocess_1,)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)])
