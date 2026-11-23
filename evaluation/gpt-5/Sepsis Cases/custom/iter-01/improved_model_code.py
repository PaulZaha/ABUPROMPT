from generator.model_generator import ModelGenerator

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
blood_cultures = gen.activity('Blood Cultures')

# Safety and standardization steps for antibiotics
sepsis_order_set = gen.activity('Use Sepsis Order Set')
allergy_check = gen.activity('Allergy Check')
renal_check = gen.activity('Renal Function Check')
abx_select_dose = gen.activity('Antibiotic Selection and Dose')
pharm_verify = gen.activity('Pharmacist Verification')
barcode_admin_check = gen.activity('Barcode Medication Administration Check')

# Fluid safety check
fluid_contra_check = gen.activity('Fluid Contraindication Check')

# Treatments
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Non-sepsis clinical path
physician_assessment = gen.activity('General ER Physician Assessment')

# Sepsis bundle: enforce correct sequence to prevent wrong treatments
sepsis_bundle = gen.partial_order(dependencies=[
    # Standardize and gate the bundle
    (sepsis_order_set, leucocytes),
    (sepsis_order_set, crp),
    (sepsis_order_set, lacticacid),
    (sepsis_order_set, blood_cultures),
    (sepsis_order_set, allergy_check),
    (sepsis_order_set, renal_check),
    (sepsis_order_set, fluid_contra_check),

    # Antibiotic safety chain
    (allergy_check, abx_select_dose),
    (renal_check, abx_select_dose),
    (abx_select_dose, pharm_verify),
    (pharm_verify, barcode_admin_check),
    (barcode_admin_check, iv_antibiotics),
    (blood_cultures, iv_antibiotics),

    # Fluid safety dependency
    (fluid_contra_check, iv_liquid)
])

# Decision after sepsis triage: sepsis bundle vs. non-sepsis assessment
decision_after_triage = gen.xor(sepsis_bundle, physician_assessment)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, decision_after_triage)
])