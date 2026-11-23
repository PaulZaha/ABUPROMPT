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
# Authorization step added to improve external quality and governance
delete_auth = gen.activity('DELETE AUTH')

# Coding validation loop: validate codes; if diagnosis changes, re-validate
coding_validation = gen.loop(code_ok, change_diagn)

# Main operational flow: validated coding -> finalize -> release -> bill
main_flow = gen.partial_order(dependencies=[(coding_validation, fin), (fin, release), (release, billed)])

# Controlled deletion path with authorization
deletion_flow = gen.partial_order(dependencies=[(delete_auth, delete)])

# Exclusive choice between authorized deletion or the main flow, after creation
choice = gen.xor(deletion_flow, main_flow)

final_model = gen.partial_order(dependencies=[(new, choice)])