from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Controlled coding/rework: run CODE OK at least once; if CHANGE DIAGN occurs, repeat CODE OK
coding_loop = gen.loop(code_ok, change_diagn)

# Mandatory, quality-gated sequence before billing
main_sequence = gen.partial_order(dependencies=[
    (release, coding_loop),
    (coding_loop, fin),
    (fin, billed)
])

# After NEW, either delete early or follow the standardized main process (no global skip)
post_new_choice = gen.xor(delete, main_sequence)

final_model = gen.partial_order(dependencies=[(new, post_new_choice)] )