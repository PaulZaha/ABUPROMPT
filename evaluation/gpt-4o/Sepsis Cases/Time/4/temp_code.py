
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

# Modified subprocess_0 to ensure 'Leucocytes' and 'CRP' run concurrently, with optional 'LacticAcid'
subprocess_0 = gen.partial_order(dependencies=[(leucocytes,), (crp,), (gen.xor(None, lacticacid),)])
# Removed strict dependency between 'IV Liquid' and 'IV Antibiotics'
subprocess_1 = gen.xor(None, gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)]))
# Combining subprocess_0 and subprocess_1 into a partial order for full concurrency when subprocess_1 is needed
subprocess_2 = gen.partial_order(dependencies=[(subprocess_0,), (subprocess_1,)])

subprocess_3 = gen.xor(None, subprocess_2)

# The main process order, ensuring steps are sequential only where necessary
final_model = gen.partial_order(dependencies=[(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_3)])
