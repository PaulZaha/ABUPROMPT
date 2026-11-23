from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
er_registration = gen.activity('ER Registration')
er_triage_sepsis = gen.activity('ER Triage & Sepsis Screening')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Optional diagnostics (order only when indicated)
crp_opt = gen.xor(None, crp)
lact_opt = gen.xor(None, lacticacid)

# Optional treatments; if both are chosen, do fluids before antibiotics
iv_liquid_opt = gen.xor(None, iv_liquid)
iv_antibiotics_opt = gen.xor(None, iv_antibiotics)

# Combine labs (Leucocytes mandatory if this path is chosen; CRP and Lactate optional)
# Treatments can start after the core lab draw (Leucocytes). If both fluids and antibiotics are used, enforce IV Liquid -> IV Antibiotics.
care_po = gen.partial_order(dependencies=[
    (leucocytes,),
    (crp_opt,),
    (lact_opt,),
    (iv_liquid_opt,),
    (iv_antibiotics_opt,),
    # Start treatments after core blood draw
    (leucocytes, iv_liquid_opt),
    (leucocytes, iv_antibiotics_opt),
    # If both treatments are selected, do fluids before antibiotics
    (iv_liquid_opt, iv_antibiotics_opt)
])

# Alternative for clear-cut/high-certainty cases: immediate antibiotics without labs
iv_antibiotics_direct = iv_antibiotics.copy()

# Post-triage decision: skip all, do labs/treatments per care_po, or give immediate antibiotics only
post_triage_decision = gen.xor(None, care_po, iv_antibiotics_direct)

# Full process: Registration -> Triage & Sepsis Screening -> Post-triage decision
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage_sepsis),
    (er_triage_sepsis, post_triage_decision)
])