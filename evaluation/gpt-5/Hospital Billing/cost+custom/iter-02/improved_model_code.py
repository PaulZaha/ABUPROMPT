from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Quality assurance loop: run CODE OK; if corrections are needed, CHANGE DIAGN triggers rework, then re-check
qa_loop = gen.loop(code_ok, change_diagn)

# Billing is optional but only allowed after RELEASE
billing_opt = gen.xor(None, billed)

# Main path: validate codes, then release, then optionally bill
main_path = gen.partial_order(dependencies=[(qa_loop, release), (release, billing_opt)])

# Decide to cancel or proceed with the main path
decision = gen.xor(delete, main_path)

# Full process: NEW -> decision -> FIN
final_model = gen.partial_order(dependencies=[(new, decision), (decision, fin)])