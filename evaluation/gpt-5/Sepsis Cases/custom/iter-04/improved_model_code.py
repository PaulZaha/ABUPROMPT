from generator.model_generator import ModelGenerator

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Existing diagnostics and therapies
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# New safety/decision activities to reduce wrong treatments
sepsis_protocol_activation = gen.activity('Sepsis Protocol Activation')
blood_cultures = gen.activity('Blood Cultures')
abx_safety_selection = gen.activity('Antibiotic Safety & Selection')
fluid_contra_check = gen.activity('Contraindication Check for IV Fluids')
pharmacist_verification = gen.activity('Pharmacist Verification (Antibiotics)')
observation = gen.activity('Clinical Reassessment / Observation')

# Optional pharmacist verification as an additional safety barrier
opt_pharmacist = gen.xor(None, pharmacist_verification)

# Sepsis path: standardize and add safety gates; run diagnostics concurrently; enforce key dependencies
sepsis_path = gen.partial_order(dependencies=[
    # Activate protocol before downstream actions
    (sepsis_protocol_activation, leucocytes),
    (sepsis_protocol_activation, crp),
    (sepsis_protocol_activation, lacticacid),
    (sepsis_protocol_activation, blood_cultures),
    (sepsis_protocol_activation, fluid_contra_check),
    (sepsis_protocol_activation, abx_safety_selection),
    (sepsis_protocol_activation, opt_pharmacist),
    # Safety checks before therapies
    (fluid_contra_check, iv_liquid),
    (abx_safety_selection, iv_antibiotics),
    (blood_cultures, iv_antibiotics),
    (opt_pharmacist, iv_antibiotics)
])

# Non-sepsis path: no automatic antibiotics/fluids; observe and reassess
non_sepsis_path = gen.partial_order(dependencies=[(observation,)])

# Decision gate after sepsis triage
post_triage_decision = gen.xor(sepsis_path, non_sepsis_path)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, post_triage_decision)
])