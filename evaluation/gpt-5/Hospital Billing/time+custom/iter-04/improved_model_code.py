from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
code_ok = gen.activity('CODE OK')
release = gen.activity('RELEASE')
billed = gen.activity('BILLED')
fin = gen.activity('FIN')

# Optional change of diagnosis before quality gate
opt_change = gen.xor(None, change_diagn)

# Quality gate with fast revalidation (repeatable from 1..n)
code_gate = gen.loop(code_ok, None)

# Main processing path: opt_change -> CODE OK -> RELEASE -> BILLED -> FIN
process_path = gen.partial_order(dependencies=[
    (opt_change, code_gate),
    (code_gate, release),
    (release, billed),
    (billed, fin)
])

# After NEW: either DELETE or follow the processing path
post_new = gen.xor(delete, process_path)

final_model = gen.partial_order(dependencies=[(new, post_new)])