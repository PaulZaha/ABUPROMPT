from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Optional, parallelizable tasks
opt_change_diagn = gen.xor(None, change_diagn)
opt_release = gen.xor(None, release)
# Early billing enabled: if this branch is chosen, perform CODE OK then BILLED
code_then_billed = gen.xor(None, gen.partial_order(dependencies=[(code_ok, billed)]))

# Main processing runs tasks in parallel where possible
process_path = gen.partial_order(dependencies=[(fin,), (opt_change_diagn,), (opt_release,), (code_then_billed,)])

# Decision after NEW: skip, delete, or process
choice_after_new = gen.xor(None, delete, process_path)

final_model = gen.partial_order(dependencies=[(new, choice_after_new)])