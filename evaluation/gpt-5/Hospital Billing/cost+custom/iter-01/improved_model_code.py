from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Validate coding; any diagnosis change triggers re-validation
review_and_correct = gen.loop(code_ok, change_diagn)

# Quality-gated main flow: validate -> release -> bill -> finalize
main_flow = gen.partial_order(dependencies=[
    (review_and_correct, release),
    (release, billed),
    (billed, fin)
])

# Early decision: either delete invalid items or proceed with controlled flow (no silent skip)
proceed_or_delete = gen.xor(delete, main_flow)

final_model = gen.partial_order(dependencies=[(new, proceed_or_delete)])