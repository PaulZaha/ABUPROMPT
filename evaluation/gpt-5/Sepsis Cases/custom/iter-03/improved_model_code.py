from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# New safety/decision activities to reduce wrong treatments
physician_assessment = gen.activity('Physician Assessment')
sepsis_confirmation = gen.activity('Sepsis Confirmation')
allergy_check = gen.activity('Allergy/Contraindications Check')
weight_measurement = gen.activity('Weight Measurement')
dose_calc = gen.activity('Dose Calculation & Verification')
abx_selection = gen.activity('Antibiotic Selection per Guideline')
blood_cultures = gen.activity('Blood Cultures')
pharm_verification = gen.activity('Pharmacist Verification')
observation = gen.activity('Observation & Reassessment')

# Lab panel is now mandatory and concurrent
labs_panel = gen.partial_order(dependencies=[(leucocytes,), (crp,), (lacticacid,)])

# Assessment and decision: labs + physician assessment -> sepsis confirmation
assessment_decision = gen.partial_order(
    dependencies=[
        (physician_assessment,),
        (labs_panel,),
        (sepsis_confirmation,),
        (physician_assessment, sepsis_confirmation),
        (labs_panel, sepsis_confirmation)
    ]
)

# Optional pharmacist verification, but if present it must precede antibiotics
pharm_opt = gen.xor(None, pharm_verification)

# Treatment path with enforced safety and sequencing
# - Blood cultures before antibiotics
# - Fluids before antibiotics (when treatment chosen)
# - Allergy check -> guideline selection -> dose calculation -> antibiotics
# - Optional pharmacist verification before antibiotics
treatment_path = gen.partial_order(
    dependencies=[
        (iv_liquid, iv_antibiotics),
        (blood_cultures, iv_antibiotics),
        (allergy_check, abx_selection),
        (abx_selection, dose_calc),
        (weight_measurement, dose_calc),
        (dose_calc, iv_antibiotics),
        (pharm_opt, iv_antibiotics)
    ]
)

# After confirmation, decide exclusively: treat or observe
post_confirmation = gen.xor(observation, treatment_path)

# Enforce sequence: assessment & decision before the post-confirmation branch
assess_then_branch = gen.partial_order(dependencies=[(assessment_decision, post_confirmation)])

# Full process
final_model = gen.partial_order(
    dependencies=[
        (er_registration, er_triage),
        (er_triage, er_sepsis_triage),
        (er_sepsis_triage, assess_then_branch)
    ]
)