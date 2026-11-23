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

# Optional lactic acid
lactic_opt = gen.xor(None, lacticacid)

# Treatment tasks run in parallel (no enforced order) and are optional as a group
treatment_parallel = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])
treatment_opt = gen.xor(None, treatment_parallel)

# Sepsis bundle: labs (mandatory when bundle chosen) + optional treatment in parallel
sepsis_bundle = gen.partial_order(dependencies=[(leucocytes,), (crp,), (lactic_opt,), (treatment_opt,)])
sepsis_bundle_opt = gen.xor(None, sepsis_bundle)

# Start sepsis bundle at ER Triage in parallel with ER Sepsis Triage
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_triage, sepsis_bundle_opt)
])