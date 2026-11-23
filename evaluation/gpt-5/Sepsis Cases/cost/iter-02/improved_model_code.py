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

# Optional specialized sepsis triage to avoid unnecessary effort for low-risk cases
opt_sepsis_triage = gen.xor(None, er_sepsis_triage)

# Labs: Leucocytes first, CRP optional
opt_crp = gen.xor(None, crp)

# Therapy options: None, IV fluids only, or lactate-guided antibiotics
therapy_liquid_only = iv_liquid.copy()
therapy_abx = gen.partial_order(dependencies=[(lacticacid, iv_liquid), (iv_liquid, iv_antibiotics)])
therapy_choice = gen.xor(None, therapy_liquid_only, therapy_abx)

# Ensure therapy is only considered after initial labs (and optional CRP)
labs_and_therapy = gen.partial_order(dependencies=[(leucocytes, opt_crp), (leucocytes, therapy_choice), (opt_crp, therapy_choice)])

# Make the entire post-triage care optional based on clinical necessity
optional_care = gen.xor(None, labs_and_therapy)

final_model = gen.partial_order(dependencies=[(er_registration, er_triage), (er_triage, opt_sepsis_triage), (opt_sepsis_triage, optional_care)])