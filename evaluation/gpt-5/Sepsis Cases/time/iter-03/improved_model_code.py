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

# Labs: draw in parallel; lactic acid remains optional
labs_lactic_opt = gen.xor(None, lacticacid)
labs_block = gen.partial_order(dependencies=[(leucocytes,), (crp,), (labs_lactic_opt,)])
labs_block_opt = gen.xor(None, labs_block)

# Treatments: make each independently optional and concurrent
iv_liquid_opt = gen.xor(None, iv_liquid)
iv_antibiotics_opt = gen.xor(None, iv_antibiotics)

# Final model: parallelize where safe, remove unnecessary dependencies
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_triage, labs_block_opt),           # labs can start right after triage
    (er_triage, iv_liquid_opt),            # fluids can start right after triage (optional)
    (er_sepsis_triage, iv_antibiotics_opt) # antibiotics start after sepsis triage (optional)
])