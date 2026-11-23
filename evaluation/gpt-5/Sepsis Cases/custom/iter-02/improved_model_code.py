from generator.model_generator import ModelGenerator

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
blood_cultures = gen.activity('Blood Cultures')

iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

activate_protocol = gen.activity('Activate Sepsis Protocol')
allergy_check = gen.activity('Allergy Check')
antibiotic_indication = gen.activity('Antibiotic Indication Check')
antibiotic_order = gen.activity('Antibiotic Order & Dose')
pharmacist_verify = gen.activity('Pharmacist Verification')
fluid_check = gen.activity('Fluid Contraindication Check')
document_no_fluids = gen.activity('Document Fluid Contraindication')
clinical_observation = gen.activity('Clinical Observation / Alternative Dx')
reassess = gen.activity('Reassess Patient and Adjust Therapy')

fluids_path = gen.partial_order(dependencies=[(fluid_check, iv_liquid)])
fluids_branch = gen.xor(document_no_fluids, fluids_path)

reassess_loop = gen.loop(reassess, None)

sepsis_path = gen.partial_order(dependencies=[
    (activate_protocol, leucocytes),
    (activate_protocol, crp),
    (activate_protocol, lacticacid),
    (activate_protocol, blood_cultures),
    (activate_protocol, antibiotic_indication),
    (activate_protocol, allergy_check),
    (activate_protocol, fluids_branch),
    (antibiotic_indication, antibiotic_order),
    (allergy_check, antibiotic_order),
    (antibiotic_order, pharmacist_verify),
    (pharmacist_verify, iv_antibiotics),
    (blood_cultures, iv_antibiotics),
    (iv_antibiotics, reassess_loop)
])

non_sepsis_path = gen.partial_order(dependencies=[(clinical_observation,)])

decision = gen.xor(non_sepsis_path, sepsis_path)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, decision)
])