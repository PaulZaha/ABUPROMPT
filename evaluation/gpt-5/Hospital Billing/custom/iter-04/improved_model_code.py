from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')
qa_review = gen.activity('QA REVIEW')

# Quality gate: coding must be checked and reviewed before release
do_block = gen.partial_order(dependencies=[(code_ok, qa_review)])
qa_loop = gen.loop(do_block, change_diagn)

# Mandatory, ordered processing path for non-deleted cases
process_path = gen.partial_order(dependencies=[(fin, qa_loop), (qa_loop, release), (release, billed)])

# After NEW, either DELETE or follow the full quality-assured processing path
main_choice = gen.xor(delete, process_path)

final_model = gen.partial_order(dependencies=[(new, main_choice)])