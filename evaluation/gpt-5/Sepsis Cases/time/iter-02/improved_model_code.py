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

# Optional Lactic Acid test
lacticacid_opt = gen.xor(None, lacticacid)

# IV therapy parallelization (fluids and antibiotics can proceed concurrently)
therapy_parallel = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])
# Therapy remains optional inside the bundle
therapy_opt = gen.xor(None, therapy_parallel)

# Sepsis bundle: labs (parallel, with optional LacticAcid) and optional therapy run in parallel
sepsis_parallel = gen.partial_order(dependencies=[(leucocytes,), (crp,), (lacticacid_opt,), (therapy_opt,)])
# Entire sepsis bundle remains optional after Sepsis Triage
sepsis_bundle_opt = gen.xor(None, sepsis_parallel)

# Overall flow: Registration -> Triage -> Sepsis Triage -> optional parallel sepsis bundle
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, sepsis_bundle_opt)
])