from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Coding quality gate: every diagnosis change triggers a re-check
coding_cycle = gen.loop(code_ok, change_diagn)

# Billing may be optional depending on case type
billed_opt = gen.xor(None, billed)

# Processing path: prepare release in parallel with coding; bill only after both; finalize after billing decision
processing = gen.partial_order(dependencies=[
    (coding_cycle, billed_opt),
    (release, billed_opt),
    (billed_opt, fin)
])

# After NEW, either delete the case or process it
post_new = gen.xor(delete, processing)

final_model = gen.partial_order(dependencies=[(new, post_new)])