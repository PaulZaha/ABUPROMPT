from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Improvement 1: Couple diagnosis changes with re-validation via a loop
quality_loop = gen.loop(code_ok, change_diagn)

# Improvement 3: Optional billing executed after release, possibly in parallel with finalization
billing_opt = gen.xor(None, billed)

# Improvement 2 + 4: Explicit, flattened main path with clear dependencies and safe parallelization
main_path = gen.partial_order(
    dependencies=[
        (quality_loop,), (release,), (fin,), (billing_opt,),
        (quality_loop, release),  # validate before release
        (release, fin),           # finalize after release
        (release, billing_opt)    # billing can start after release, parallel with finalization
    ]
)

# Improvement 5: Early choice to avoid unnecessary work
post_new_choice = gen.xor(None, delete, main_path)

final_model = gen.partial_order(dependencies=[(new, post_new_choice)])