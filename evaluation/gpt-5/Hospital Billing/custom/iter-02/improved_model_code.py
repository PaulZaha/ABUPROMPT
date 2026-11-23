from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
code_ok = gen.activity('CODE OK')
release = gen.activity('RELEASE')
billed = gen.activity('BILLED')
cancel_notice = gen.activity('CANCEL NOTICE')

# Allow 0..n diagnosis changes before finalization
change_loop = gen.loop(None, change_diagn)

# Billing is optional and only after release
optional_billing = gen.xor(None, billed)

# Main quality-assured sequence: CHANGE DIAGN* -> FIN -> CODE OK -> RELEASE -> (optional) BILLED
main_seq = gen.partial_order(dependencies=[
    (change_loop, fin),
    (fin, code_ok),
    (code_ok, release),
    (release, optional_billing)
])

# Explicit cancellation path with external notification
cancel_path = gen.partial_order(dependencies=[
    (delete, cancel_notice)
])

# After NEW, explicitly choose either cancel or process
post_new = gen.xor(cancel_path, main_seq)

final_model = gen.partial_order(dependencies=[(new, post_new)])