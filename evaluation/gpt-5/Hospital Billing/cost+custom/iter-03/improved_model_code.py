from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Localized rework: validate coding; if not OK, adjust diagnosis and re-validate
coding_rework = gen.loop(code_ok, change_diagn)

# Main straight-through path: RELEASE -> (validate/rework) -> FIN -> BILLED
process_path = gen.partial_order(dependencies=[(release, coding_rework), (coding_rework, fin), (fin, billed)])

# Early explicit decision: cancel or process (no silent skip)
post_new = gen.xor(delete, process_path)

final_model = gen.partial_order(dependencies=[(new, post_new)])