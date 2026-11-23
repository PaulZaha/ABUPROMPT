from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Validate first; only if validation fails, correct diagnosis and re-validate
quality_cycle = gen.loop(code_ok, change_diagn)

# Main processing: release -> validated coding -> billing
process_core = gen.partial_order(dependencies=[(release, quality_cycle), (quality_cycle, billed)])

# Decide early: delete or process
branch = gen.xor(delete, process_core)

# Always finalize after chosen branch
final_model = gen.partial_order(dependencies=[(new, branch), (branch, fin)])