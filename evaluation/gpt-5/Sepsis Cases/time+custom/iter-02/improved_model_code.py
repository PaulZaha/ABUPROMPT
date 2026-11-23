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
antibiotic_safety_check = gen.activity('Antibiotic Safety Check')

optional_crp = gen.xor(None, crp)

sepsis_bundle = gen.partial_order(dependencies=[
    (leucocytes,),
    (lacticacid,),
    (optional_crp,),
    (iv_liquid,),
    (antibiotic_safety_check, iv_antibiotics)
])

sepsis_choice = gen.xor(sepsis_bundle, None)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, sepsis_choice)
])