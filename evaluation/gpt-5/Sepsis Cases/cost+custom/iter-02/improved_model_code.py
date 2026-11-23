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
antibiotic_indication_check = gen.activity('Antibiotic Indication Check')
antibiotic_allergy_check = gen.activity('Antibiotic Allergy Check')

# Optional lactate test only when treatment is indicated
lactate_optional = gen.xor(None, lacticacid)

# If antibiotics are indicated: ensure IV fluids precede antibiotics and allergy check gates antibiotics
indicated_subprocess = gen.partial_order(dependencies=[
    (iv_liquid, antibiotic_allergy_check),
    (antibiotic_allergy_check, iv_antibiotics),
    (lactate_optional, iv_antibiotics)
])

# After indication check, either proceed with indicated treatment path or skip
post_check = gen.xor(None, indicated_subprocess)

# Sepsis management path: run labs in parallel, then indication check, then (optionally) treatment
sepsis_management = gen.partial_order(dependencies=[
    (leucocytes, antibiotic_indication_check),
    (crp, antibiotic_indication_check),
    (antibiotic_indication_check, post_check)
])

# After ER sepsis triage, either no sepsis management (skip) or follow sepsis management path
sepsis_branch = gen.xor(None, sepsis_management)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, sepsis_branch)
])