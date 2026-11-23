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

# New activities to reduce wrong treatments
interpret_labs = gen.activity('Interpret Sepsis Labs')
blood_cultures = gen.activity('Blood Cultures')
allergy_check = gen.activity('Allergy & Contraindication Check')
antibiotic_selection = gen.activity('Antibiotic Selection per Guidelines')
dose_calc_verify = gen.activity('Antibiotic Dose Calculation & Verification')
second_check = gen.activity('Second Clinician Double-Check')
fluid_assessment = gen.activity('Fluid Responsiveness Assessment')
alternative_management = gen.activity('Alternative Management (No Antibiotics)')
observation = gen.activity('Clinical Observation and Reassessment')

# Suspected sepsis: mandatory labs concurrently, then interpret
labs_suspected = gen.partial_order(dependencies=[
    (leucocytes, interpret_labs),
    (crp, interpret_labs),
    (lacticacid, interpret_labs)
])

# Pre-antibiotic safety and stewardship chain; blood cultures must precede administration
antibiotic_path = gen.partial_order(dependencies=[
    (allergy_check, antibiotic_selection),
    (antibiotic_selection, dose_calc_verify),
    (dose_calc_verify, second_check),
    (blood_cultures, iv_antibiotics),
    (second_check, iv_antibiotics)
])

# Fluids are optional and gated by fluid responsiveness assessment
fluid_mandatory = gen.partial_order(dependencies=[(fluid_assessment, iv_liquid)])
fluid_optional = gen.xor(None, fluid_mandatory)

# Treatment package can execute antibiotic path and (optionally) fluids in parallel after evaluation
treat_package = gen.partial_order(dependencies=[
    (antibiotic_path,),
    (fluid_optional,)
])

# After labs and interpretation, decide between treatment or alternative management
decision_xor = gen.xor(treat_package, alternative_management)

# Full suspected sepsis path: labs -> decision
suspected_model = gen.partial_order(dependencies=[(labs_suspected, decision_xor)])

# Post-triage exclusive choice: suspected sepsis vs observation
post_triage_xor = gen.xor(suspected_model, observation)

# Final model
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, post_triage_xor)
])