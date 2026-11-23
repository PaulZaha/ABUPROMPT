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

# Optional diagnostics, executed only when sepsis path is taken
leucocytes_opt = gen.xor(None, leucocytes)
crp_opt = gen.xor(None, crp)
lacticacid_opt = gen.xor(None, lacticacid)

# Sepsis care: triage precedes, then labs and IV start in parallel; antibiotics after IV access/fluids
sepsis_path = gen.partial_order(dependencies=[
    (er_sepsis_triage, leucocytes_opt),
    (er_sepsis_triage, crp_opt),
    (er_sepsis_triage, lacticacid_opt),
    (er_sepsis_triage, iv_liquid),
    (iv_liquid, iv_antibiotics)
])

# Gate: execute sepsis path only when indicated
sepsis_gate = gen.xor(None, sepsis_path)

final_model = gen.partial_order(dependencies=[(er_registration, er_triage), (er_triage, sepsis_gate)])