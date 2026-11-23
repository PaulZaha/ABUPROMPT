from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Intake and triage
_er_registration = gen.activity('ER Registration')
_er_triage = gen.activity('ER Triage')
_er_sepsis_triage = gen.activity('ER Sepsis Triage')

# Diagnostics and treatments
_leucocytes = gen.activity('Leucocytes')
_crp = gen.activity('CRP')
_lacticacid = gen.activity('LacticAcid')
_iv_liquid = gen.activity('IV Liquid')
_iv_antibiotics = gen.activity('IV Antibiotics')

# Added safety and speed enablers
_iv_access = gen.activity('IV Access & Blood Draw')
_abx_order_check = gen.activity('ABX Order & Allergy Check')
_blood_cultures = gen.activity('Blood Cultures')

# Allow 0..n fluid boluses without blocking antibiotics
_fluid_boluses = gen.loop(None, _iv_liquid)

# Sepsis bundle: make labs concurrent and start treatment ASAP after IV access
_sepsis_bundle = gen.partial_order(dependencies=[
    (_iv_access, _leucocytes),
    (_iv_access, _crp),
    (_iv_access, _lacticacid),   # lactate mandatory in sepsis path
    (_iv_access, _blood_cultures),
    (_iv_access, _fluid_boluses),
    (_abx_order_check, _iv_antibiotics),  # safety check before antibiotics
    (_iv_access, _iv_antibiotics),        # IV access needed for antibiotics
    (_abx_order_check,),                  # include as node (can run in parallel with IV access)
])

# Non-sepsis path: optional basic labs only, no antibiotics/fluids
_non_sepsis_labs = gen.partial_order(dependencies=[(_leucocytes.copy(),), (_crp.copy(),)])
_non_sepsis_path = gen.xor(None, _non_sepsis_labs)

# Decision after sepsis triage: suspected sepsis vs. no sepsis
_post_triage = gen.xor(_sepsis_bundle, _non_sepsis_path)

# Overall process sequence
final_model = gen.partial_order(dependencies=[
    (_er_registration, _er_triage),
    (_er_triage, _er_sepsis_triage),
    (_er_sepsis_triage, _post_triage)
])