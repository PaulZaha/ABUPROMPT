from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')

leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Sepsis path: mandatory diagnostics before treatment; allow lactate re-measurement if indicated
lactate_loop = gen.loop(lacticacid, None)  # repeat Lactate 1..n times
sepsis_path = gen.partial_order(dependencies=[
    # Diagnostics must complete before either treatment step starts
    (leucocytes, iv_liquid),
    (crp, iv_liquid),
    (lactate_loop, iv_liquid),
    (leucocytes, iv_antibiotics),
    (crp, iv_antibiotics),
    (lactate_loop, iv_antibiotics)
])

# Non-sepsis path: no antibiotics; minimal diagnostics and fluids are optional
leucocytes_ns = leucocytes.copy()
crp_ns = crp.copy()
iv_liquid_ns = iv_liquid.copy()

leucocytes_opt = gen.xor(None, leucocytes_ns)
crp_opt = gen.xor(None, crp_ns)
iv_liquid_opt = gen.xor(None, iv_liquid_ns)

non_sepsis_path = gen.partial_order(dependencies=[
    (leucocytes_opt,),
    (crp_opt,),
    (iv_liquid_opt,)
])

# Decision based on sepsis assessment
post_triage = gen.xor(sepsis_path, non_sepsis_path)

# Overall process
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage),
    (er_triage, er_sepsis_triage),
    (er_sepsis_triage, post_triage)
])