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

# Make cost-driving tasks optional and enable early parallelization after ER Triage
leucocytes_opt = gen.xor(None, leucocytes)
crp_opt = gen.xor(None, crp)
lactate_opt = gen.xor(None, lacticacid)
iv_liquid_opt = gen.xor(None, iv_liquid)
iv_antibiotics_opt = gen.xor(None, iv_antibiotics)

# Final model: labs and IV fluids start in parallel after ER Triage; antibiotics start right after ER Sepsis Triage
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_triage, leucocytes_opt),
    (er_triage, crp_opt),
    (er_triage, lactate_opt),
    (er_triage, iv_liquid_opt),
    (er_sepsis_triage, iv_antibiotics_opt)
])