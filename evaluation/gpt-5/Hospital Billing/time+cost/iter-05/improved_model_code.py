from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Optional change of diagnosis
change_diagn_opt = gen.xor(None, change_diagn)

# Optional verification and release: ensure CODE OK precedes RELEASE
release_chain = gen.xor(None, gen.partial_order(dependencies=[(code_ok, release)]))

# Optional billing
billed_opt = gen.xor(None, billed)

# Processing: after optional diagnosis change, run FIN and the optional CODE OK->RELEASE chain in parallel;
# Billing occurs after FIN and (if executed) the release chain.
processing = gen.partial_order(dependencies=[
    (change_diagn_opt, fin),
    (change_diagn_opt, release_chain),
    (fin, billed_opt),
    (release_chain, billed_opt)
])

# After NEW, choose to skip, DELETE, or proceed with processing
post_new = gen.xor(None, delete, processing)

final_model = gen.partial_order(dependencies=[(new, post_new)])