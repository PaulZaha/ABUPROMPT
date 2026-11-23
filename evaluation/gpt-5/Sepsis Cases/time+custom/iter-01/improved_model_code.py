from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core patient flow
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')

# Treatments and safety checks
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')
blood_cultures = gen.activity('Blood Cultures')
abx_allergy_check = gen.activity('Antibiotic Allergy Check')

# Sepsis bundle: parallelize labs and IV fluids; gate antibiotics by cultures and allergy check
sepsis_bundle = gen.partial_order(dependencies=[
    (leucocytes,),
    (crp,),
    (lacticacid,),
    (iv_liquid,),
    (blood_cultures, iv_antibiotics),
    (abx_allergy_check, iv_antibiotics)
])

# Execute sepsis bundle only if ER Sepsis Triage indicates sepsis
post_triage_path = gen.xor(None, sepsis_bundle)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, post_triage_path)
])