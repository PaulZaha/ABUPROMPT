from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core pathway
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')

# Treatments
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Make individual labs optional and concurrent
leucocytes_opt = gen.xor(None, leucocytes)
crp_opt = gen.xor(None, crp)
lacticacid_opt = gen.xor(None, lacticacid)

labs_concurrent = gen.partial_order(dependencies=[(leucocytes_opt,), (crp_opt,), (lacticacid_opt,)])
labs_block = gen.xor(None, labs_concurrent)

# Run IV fluids and antibiotics in parallel; treatment as an optional block
therapy_parallel = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])
therapy_block = gen.xor(None, therapy_parallel)

# Final model: start labs after ER triage and in parallel with sepsis triage; start therapy after sepsis triage
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_triage, labs_block),
    (er_sepsis_triage, therapy_block)
])