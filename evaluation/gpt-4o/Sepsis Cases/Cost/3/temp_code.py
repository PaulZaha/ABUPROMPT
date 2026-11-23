
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

# Update subprocess_0 based on improvement plan
subprocess_0 = gen.xor(None, lacticacid)

# Update the subprocess_1 to execute iv_liquid only if lacticacid indicates dehydration
subprocess_1 = gen.xor(None, gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)]))

# Updated subprocess_2 to have crp only if leucocytes indicate necessity
subprocess_2 = gen.xor(leucocytes, gen.partial_order(dependencies=[(crp,), (subprocess_0,)]))

# Reflect improvements in subprocess_3 based on lacticacid or sepsis triage needs
subprocess_3 = gen.xor(None, subprocess_1)

subprocess_4 = gen.partial_order(dependencies=[(subprocess_2, subprocess_3)])

subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies=[(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)])
