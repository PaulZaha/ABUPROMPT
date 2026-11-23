from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core ER flow
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

# Moderate-risk path: stepwise, conditional labs and granular treatment
cond_crp = gen.xor(None, crp)                    # order CRP only if needed
cond_lactate = gen.xor(None, lacticacid)         # order Lactate only if needed

# Treatment options for moderate risk: None, Fluids only, Fluids -> Antibiotics
iv_liquid_for_sequence_moderate = iv_liquid.copy()
iv_antibiotics_for_sequence_moderate = iv_antibiotics.copy()
sequence_moderate = gen.partial_order(dependencies=[(iv_liquid_for_sequence_moderate, iv_antibiotics_for_sequence_moderate)])
moderate_treatment = gen.xor(None, iv_liquid, sequence_moderate)

# Build moderate path sequencing: Leucocytes -> optional CRP -> optional Lactate -> treatment
moderate_path = gen.partial_order(dependencies=[
    (leucocytes, cond_crp),
    (cond_crp, cond_lactate),
    (cond_lactate, moderate_treatment)
])

# High-risk path: full labs concurrently, then cost-aware treatment choice
leucocytes_high = leucocytes.copy()
crp_high = crp.copy()
lacticacid_high = lacticacid.copy()

iv_liquid_high_for_sequence = iv_liquid.copy()
iv_antibiotics_high = iv_antibiotics.copy()
sequence_high = gen.partial_order(dependencies=[(iv_liquid_high_for_sequence, iv_antibiotics_high)])
iv_liquid_high_only = iv_liquid.copy()

# For high risk, choose fluids-only or fluids+antibiotics (no skip at this risk level)
high_treatment = gen.xor(sequence_high, iv_liquid_high_only)

# Labs run concurrently; treatment follows after labs
high_path = gen.partial_order(dependencies=[
    (leucocytes_high, high_treatment),
    (crp_high, high_treatment),
    (lacticacid_high, high_treatment)
])

# Risk-based branching after sepsis triage: low-risk skip, moderate risk stepwise, high risk concurrent full panel
risk_branch = gen.xor(None, moderate_path, high_path)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, risk_branch)
])