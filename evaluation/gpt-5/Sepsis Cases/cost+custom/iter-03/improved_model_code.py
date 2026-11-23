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

sepsis_screen = gen.activity('Sepsis Screening (qSOFA/SIRS)')
blood_cultures = gen.activity('Blood Cultures')
abx_review = gen.activity('Antibiotic Indication Review')
allergy_check = gen.activity('Antibiotic Allergy & Contraindication Check')
observation = gen.activity('Observation & Reassessment')

lactate_opt = gen.xor(None, lacticacid)
iv_liquid_opt = gen.xor(None, iv_liquid)

suspected_sepsis_path = gen.partial_order(dependencies=[
    (leucocytes, abx_review),
    (crp, abx_review),
    (lactate_opt, abx_review),
    (blood_cultures, iv_antibiotics),
    (abx_review, allergy_check),
    (allergy_check, iv_antibiotics),
    (iv_liquid_opt,)
])

non_suspected_path = gen.loop(observation, None)

branch = gen.xor(non_suspected_path, suspected_sepsis_path)

final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, sepsis_screen),
    (sepsis_screen, branch)
])