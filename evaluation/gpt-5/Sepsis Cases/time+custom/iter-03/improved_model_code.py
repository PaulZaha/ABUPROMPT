from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Entry and triage
_er_registration = gen.activity('ER Registration')
_er_triage = gen.activity('ER Triage')
_er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics and treatments
_leucocytes = gen.activity('Leucocytes')
_crp = gen.activity('CRP')
_lacticacid = gen.activity('LacticAcid')
_iv_liquid = gen.activity('IV Liquid')
_iv_antibiotics = gen.activity('IV Antibiotics')

# Safety and protocol controls
_activate_protocol = gen.activity('Activate Sepsis Protocol')
_abx_allergy_check = gen.activity('Antibiotics Allergy Check')

# Optional CRP (kept optional to save time when it does not change immediate actions)
_optional_crp = gen.xor(None, _crp)

# Sepsis-suspected branch: standard bundle with maximum safe concurrency
_sepsis_branch = gen.partial_order(dependencies=[
    (_activate_protocol, _leucocytes),
    (_activate_protocol, _optional_crp),
    (_activate_protocol, _lacticacid),
    (_activate_protocol, _iv_liquid),
    (_activate_protocol, _abx_allergy_check),
    (_abx_allergy_check, _iv_antibiotics)
])

# Decision after sepsis triage: execute bundle when sepsis suspected, otherwise skip
_decision = gen.xor(None, _sepsis_branch)

# Overall flow
final_model = gen.partial_order(dependencies=[
    (_er_registration, _er_triage),
    (_er_triage, _er_sepsis_triage),
    (_er_sepsis_triage, _decision)
])