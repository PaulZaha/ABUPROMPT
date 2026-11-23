from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core ER flow
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics and treatments (existing)
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Added controls to reduce wrong treatments and speed up execution
blood_cultures = gen.activity('Blood Cultures')
iv_access = gen.activity('IV Access')
abx_allergy_check = gen.activity('Antibiotic Allergy Check')
abx_selection = gen.activity('Select Antibiotic (Protocol)')

# Sepsis branch: maximal safe parallelism, correct sequencing
# - Repeatable lactate
lactate_loop = gen.loop(lacticacid, None)  # 1..n repeats
# - Optional fluids after IV access
maybe_fluids = gen.xor(None, iv_liquid)

sepsis_branch = gen.partial_order(dependencies=[
    # Make nodes explicit for concurrency
    (leucocytes,),
    (crp,),
    (lactate_loop,),
    (blood_cultures,),
    (iv_access,),
    (abx_allergy_check,),
    # Safety checks and proper sequence to reduce wrong antibiotics
    (abx_allergy_check, abx_selection),
    (blood_cultures, iv_antibiotics),   # cultures before antibiotics
    (iv_access, iv_antibiotics),        # require IV access
    (abx_selection, iv_antibiotics),    # give selected antibiotic
    # Fluids can start once access is in; independent of antibiotics
    (iv_access, maybe_fluids)
])

# Non-sepsis branch: no IV/antibiotics; minimal, concurrent labs
leucocytes_ns = leucocytes.copy()
crp_ns = crp.copy()
lactate_optional_ns = gen.xor(None, lacticacid.copy())

non_sepsis_branch = gen.partial_order(dependencies=[
    (leucocytes_ns,),
    (crp_ns,),
    (lactate_optional_ns,)
])

# Decision after sepsis triage
path_choice = gen.xor(non_sepsis_branch, sepsis_branch)

# End-to-end model
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, path_choice)
])