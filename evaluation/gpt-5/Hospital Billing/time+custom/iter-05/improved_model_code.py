from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Iterative quality gate: start with CODE OK; if issues are found, perform CHANGE DIAGN and re-check.
quality_rework = gen.loop(code_ok, change_diagn)

# Optional billing after release
bill_optional = gen.xor(None, billed)

# Core processing: quality gate -> RELEASE -> FIN and optional BILLED in parallel
core_process = gen.partial_order(dependencies=[(quality_rework, release), (release, fin), (release, bill_optional)])

# Decision after NEW: either DELETE or proceed with core process
path_choice = gen.xor(delete, core_process)

final_model = gen.partial_order(dependencies=[(new, path_choice)])