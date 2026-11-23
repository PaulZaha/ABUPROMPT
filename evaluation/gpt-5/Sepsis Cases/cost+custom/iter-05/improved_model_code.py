from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core ER flow
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics and treatments
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Safety and approval steps
allergy_check = gen.activity('Allergy Check')
antibiotic_approval = gen.activity('Antibiotic Approval')

# Cost- and risk-aware optionalities
crp_optional = gen.xor(None, crp)
fluids_optional = gen.xor(None, iv_liquid)
antibiotics_optional = gen.xor(None, iv_antibiotics)

# Sepsis workup and treatment path (flattened partial order, no nested partial orders)
# - LacticAcid and Leucocytes mandatory (sources)
# - CRP optional and concurrent
# - Antibiotic Approval must come after key labs (Leucocytes, LacticAcid)
# - IV Antibiotics may only occur after both Allergy Check and Antibiotic Approval
# - IV Liquid optional and concurrent (no hard prerequisite for antibiotics)
sepsis_path = gen.partial_order(dependencies=[
    (leucocytes, antibiotic_approval),
    (lacticacid, antibiotic_approval),
    (antibiotic_approval, antibiotics_optional),
    (allergy_check, antibiotics_optional),
    (crp_optional,),
    (fluids_optional,)
])

# Branch after sepsis triage: do sepsis path or skip (non-septic patients)
sepsis_decision = gen.xor(None, sepsis_path)

# Full process: registration -> triage -> sepsis triage -> (sepsis decision)
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, sepsis_decision)
])