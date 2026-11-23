from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Targeted rework: verify coding; if changes are needed, adjust diagnosis and recheck
quality_cycle = gen.loop(code_ok, change_diagn)

# Optional billing after release
billed_optional = gen.xor(None, billed)

# Use a copy of FIN inside the billable path to avoid reuse conflicts
fin_billable = fin.copy()

# Billable path: correct coding before release, then (optionally) bill, and finalize
billable_path = gen.partial_order(dependencies=[
    (quality_cycle, release),
    (release, billed_optional),
    (billed_optional, fin_billable)
])

# Non-billable path: finalize directly
non_billable_path = fin

# Decision after NEW: skip, delete, process as billable, or finalize as non-billable
post_new_choice = gen.xor(None, delete, billable_path, non_billable_path)

final_model = gen.partial_order(dependencies=[(new, post_new_choice)])