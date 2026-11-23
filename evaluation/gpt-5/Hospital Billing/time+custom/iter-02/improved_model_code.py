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

# Allow 0..n diagnosis changes before coding (batch changes to avoid repeated coding)
change_diag_loop = gen.loop(None, change_diagn)

# Core processing: concurrent FIN and CODE OK (after any diagnosis changes), then RELEASE, then BILLED
process_core = gen.partial_order(
    dependencies=[
        (change_diag_loop, code_ok),  # ensure coding after any diagnosis changes
        (fin, release),               # release only after finalization
        (code_ok, release),           # and after coding is OK
        (release, billed)             # billing only after release
    ]
)

# After NEW, either delete or fully process (no unconditional skip)
post_new = gen.xor(delete, process_core)

# Sequence: NEW -> (DELETE or PROCESS)
final_model = gen.partial_order(dependencies=[(new, post_new)])