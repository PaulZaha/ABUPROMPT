
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage') # Made mandatory
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid') # Made part of a streamlined sequence
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

subprocess_0 = gen.partial_order(dependencies=[(leucocytes, crp)]) # Managed concurrently to streamline tests
subprocess_1 = gen.partial_order(dependencies=[(lacticacid,), (subprocess_0,)])
subprocess_2 = gen.partial_order(dependencies=[(iv_liquid, iv_antibiotics)]) # Managed separately to streamline treatments
subprocess_3 = gen.partial_order(dependencies=[(subprocess_1, subprocess_2)])

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage), 
    (er_triage, er_sepsis_triage), # Updated order
    (er_sepsis_triage, subprocess_3) 
])
