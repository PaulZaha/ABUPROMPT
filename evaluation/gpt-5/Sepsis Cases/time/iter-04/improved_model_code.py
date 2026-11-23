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

# Labs block (optional), lactic acid optional
labs_lactic_optional = gen.xor(None, lacticacid)
labs_block = gen.partial_order(dependencies=[(leucocytes,), (crp,), (labs_lactic_optional,)])
labs_optional = gen.xor(None, labs_block)

# Treatment block (optional), fluids and antibiotics can run concurrently
treatment_block = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])
treatment_optional = gen.xor(None, treatment_block)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_triage, labs_optional),
    (er_triage, treatment_optional)
])