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

# Optional diagnostics/interventions to reduce cost where clinically appropriate
optional_lactate = gen.xor(None, lacticacid)  # keep lactate optional based on clinical judgment
optional_crp = gen.xor(None, crp)             # make CRP optional (non-critical for immediate action)
optional_iv_fluid = gen.xor(None, iv_liquid)  # fluids when indicated (e.g., hypotension)

# Run labs and therapy in parallel to reduce time-to-antibiotics
sepsis_parallel = gen.partial_order(dependencies=[
    (leucocytes,),
    (optional_crp,),
    (optional_lactate,),
    (optional_iv_fluid,),
    (iv_antibiotics,)
])

# Execute sepsis management only when indicated after sepsis triage
sepsis_path = gen.xor(None, sepsis_parallel)

# Allow quick registration to overlap with clinical triage; ensure pathway follows Sepsis Triage
final_model = gen.partial_order(dependencies=[
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, sepsis_path),
    (er_registration,)
])