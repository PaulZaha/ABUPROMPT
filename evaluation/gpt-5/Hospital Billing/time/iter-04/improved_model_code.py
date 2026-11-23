from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Optional blocks
opt_change_diagn = gen.xor(None, change_diagn)
release_code_ok = gen.partial_order(dependencies=[(release,), (code_ok,)])
opt_release_code_ok = gen.xor(None, release_code_ok)
opt_billed = gen.xor(None, billed)

# Run CHANGE DIAGN and (optional) RELEASE/CODE OK in parallel with FIN.
# Allow BILLED right after FIN, without waiting for optional RELEASE/CODE OK.
post_new = gen.partial_order(dependencies=[
    (opt_change_diagn,),
    (opt_release_code_ok,),
    (fin, opt_billed)
])

# After NEW, exclusive choice: skip, DELETE, or proceed with the parallel work
choice_after_new = gen.xor(None, delete, post_new)

final_model = gen.partial_order(dependencies=[(new, choice_after_new)])