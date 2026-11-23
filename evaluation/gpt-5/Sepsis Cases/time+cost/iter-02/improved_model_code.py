from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Labs: concurrent, with lactic acid optional inside the bundle
lactic_opt = gen.xor(None, lacticacid)
labs_parallel = gen.partial_order(dependencies=[(leucocytes,), (crp,), (lactic_opt,)])
labs_opt = gen.xor(None, labs_parallel)

# Treatments: optional; fluids can start after triage; antibiotics only after sepsis triage
iv_liquid_opt = gen.xor(None, iv_liquid)
iv_antibiotics_opt = gen.xor(None, iv_antibiotics)

# Final model: parallelize labs and fluids with sepsis triage; gate antibiotics by sepsis triage
final_model = gen.partial_order(
    dependencies=[
        (er_registration, er_triage),
        (er_triage, er_sepsis_triage),
        (er_triage, labs_opt),
        (er_triage, iv_liquid_opt),
        (er_sepsis_triage, iv_antibiotics_opt)
    ]
)