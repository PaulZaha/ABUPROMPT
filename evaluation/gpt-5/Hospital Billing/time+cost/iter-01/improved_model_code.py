from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Allow 0..n diagnosis adjustments before the quality gate
diag_adjust = gen.loop(None, change_diagn)

# Core streamlined path: after adjustments, perform RELEASE and CODE OK in parallel,
# then perform FIN and BILLED in parallel (both gated by RELEASE and CODE OK)
core_path = gen.partial_order(
    dependencies=[
        (diag_adjust, release),
        (diag_adjust, code_ok),
        (release, fin),
        (code_ok, fin),
        (release, billed),
        (code_ok, billed),
    ]
)

# Early decision: cancel (DELETE) or proceed with the core path
route = gen.xor(delete, core_path)

final_model = gen.partial_order(dependencies=[(new, route)])