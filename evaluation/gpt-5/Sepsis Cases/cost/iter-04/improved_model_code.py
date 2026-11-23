from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
cbc_crp_panel = gen.activity('CBC + CRP Panel')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Optional lactate (only considered in high-risk path)
optional_lactate = gen.xor(None, lacticacid)

# Path 1: No further diagnostics/treatment (skip)
# Path 2: Labs only (use combined panel to avoid duplicate blood draw)
labs_only = cbc_crp_panel.copy()

# Path 3: Labs + Treatment, with labs before treatment
labs_plus_treatment = gen.partial_order(
    dependencies=[
        (cbc_crp_panel, iv_liquid),
        (optional_lactate, iv_liquid),
        (iv_liquid, iv_antibiotics)
    ]
)

# Risk-based branching after sepsis triage
risk_based = gen.xor(None, labs_only, labs_plus_treatment)

# Final process
final_model = gen.partial_order(
    dependencies=[
        (er_registration, er_triage),
        (er_triage, er_sepsis_triage),
        (er_sepsis_triage, risk_based)
    ]
)