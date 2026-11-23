from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# If diagnosis changes, enforce CODE OK right after; otherwise skip both.
change_seq = gen.partial_order(dependencies=[(change_diagn, code_ok)])
change_optional = gen.xor(change_seq, None)

# Billing is optional and can run in parallel after RELEASE.
billed_optional = gen.xor(None, billed)

# Main processing path: optional change+QA -> release -> parallel finalization and (optional) billing
process = gen.partial_order(dependencies=[
    (change_optional, release),
    (release, fin),
    (release, billed_optional)
])

# After NEW, either DELETE or proceed with processing
choice_after_new = gen.xor(delete, process)

final_model = gen.partial_order(dependencies=[(new, choice_after_new)])