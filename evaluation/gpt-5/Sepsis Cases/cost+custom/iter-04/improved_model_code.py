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

# New/expanded activities to improve safety and cost-effectiveness
blood_cultures = gen.activity('Blood Cultures')
abx_allergy_check = gen.activity('Antibiotic Allergy Check')
abx_selection_support = gen.activity('Antibiotic Selection Support')
md_abx_approval = gen.activity('MD Approves Antibiotics')
assess_fluids = gen.activity('Assess Need for IV Fluids')
observation = gen.activity('Observation')
physician_reassess = gen.activity('Physician Reassessment')

# Optional diagnostics/treatments and controlled repetition where appropriate
opt_leucocytes_hi = gen.xor(None, leucocytes)
opt_crp_hi = gen.xor(None, crp)
lactate_loop = gen.loop(lacticacid, None)  # allow 1..n lactate measurements in high-risk
optional_iv_fluids = gen.xor(None, iv_liquid)
optional_iv_abx = gen.xor(None, iv_antibiotics)

# High-risk (sepsis-suspected) path: gated, standardized bundle
high_risk_path = gen.partial_order(dependencies=[
    (blood_cultures, optional_iv_abx),
    (abx_allergy_check, optional_iv_abx),
    (abx_selection_support, optional_iv_abx),
    (md_abx_approval, optional_iv_abx),
    (assess_fluids, optional_iv_fluids),
    (lactate_loop,),
    (opt_leucocytes_hi,),
    (opt_crp_hi,),
    (blood_cultures,),
    (abx_allergy_check,),
    (abx_selection_support,),
    (md_abx_approval,),
    (assess_fluids,),
    (optional_iv_fluids,),
    (optional_iv_abx,)
])

# Low-risk path: observation and targeted labs only; avoids lactate/antibiotics/fluids by default
opt_leucocytes_lr = gen.xor(None, leucocytes.copy())
opt_crp_lr = gen.xor(None, crp.copy())
low_risk_path = gen.partial_order(dependencies=[
    (observation, physician_reassess),
    (opt_leucocytes_lr,),
    (opt_crp_lr,)
])

# Exclusive choice based on sepsis suspicion/risk
decision = gen.xor(low_risk_path, high_risk_path)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, decision)
])