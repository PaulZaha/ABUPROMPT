
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Define the activities
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Restructure subprocess_0 to allow concurrent execution of LacticAcid, Leucocytes, and CRP
subprocess_0 = gen.partial_order(dependencies=[(leucocytes,), (crp,), (lacticacid,)])

# Subprocess for IV Liquid and IV Antibiotics, allowing for concurrent execution
subprocess_1 = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])

# Overall subprocess allowing for concurrent execution of subprocess_0 and subprocess_1
subprocess_4 = gen.partial_order(dependencies=[(subprocess_0,), (subprocess_1,)])

# Allow subprocess_4 as optional depending on condition execution
subprocess_5 = gen.xor(None, subprocess_4)

# Compile the final model with more concurrency
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, subprocess_5)
])
