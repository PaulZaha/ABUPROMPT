
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

subprocess_0 = gen.partial_order(dependencies=[(leucocytes,), (crp,), (lacticacid,)])
subprocess_1 = gen.partial_order(dependencies=[(iv_liquid, iv_antibiotics)])

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage), 
    (er_triage, er_sepsis_triage), 
    (er_sepsis_triage, subprocess_0), 
    (subprocess_0, subprocess_1)
])
