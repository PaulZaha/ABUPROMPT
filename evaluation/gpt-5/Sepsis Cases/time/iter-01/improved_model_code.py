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

# Optional lactic acid test
lactate_optional = gen.xor(None, lacticacid)

# Treatment bundle: fluids and antibiotics can run in parallel; bundle remains optional
therapy_concurrent = gen.partial_order(dependencies=[(iv_liquid,), (iv_antibiotics,)])
therapy_optional = gen.xor(None, therapy_concurrent)

# Final model: labs start right after ER Triage (in parallel with Sepsis Triage),
# treatment can start right after Sepsis Triage without waiting for labs.
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_triage, leucocytes),
    (er_triage, crp),
    (er_triage, lactate_optional),
    (er_sepsis_triage, therapy_optional)
])