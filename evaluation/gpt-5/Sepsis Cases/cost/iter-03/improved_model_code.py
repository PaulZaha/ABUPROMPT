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

# High-risk branch: Leucocytes + optional LacticAcid in parallel with IV therapy (IV Liquid -> IV Antibiotics)
lactate_optional = gen.xor(None, lacticacid)
high_risk_branch = gen.partial_order(dependencies=[(iv_liquid, iv_antibiotics), (leucocytes,), (lactate_optional,)])

# Moderate-risk branch: CRP only
moderate_risk_branch = crp

# Risk-based choice after sepsis triage: skip (low risk), CRP only (moderate risk), or high-risk branch
risk_based = gen.xor(None, moderate_risk_branch, high_risk_branch)

final_model = gen.partial_order(dependencies=[(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, risk_based)])