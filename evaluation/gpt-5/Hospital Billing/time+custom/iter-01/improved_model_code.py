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

# Optional change of diagnosis prior to verification
opt_change = gen.xor(None, change_diagn)

# Billing path: require RELEASE before BILLED, and then finalize
bill_sequence = gen.partial_order(dependencies=[(release, billed), (billed, fin)])

# No-billing path: finalize right after successful verification
fin_quick = fin.copy()
post_code_ok = gen.xor(fin_quick, bill_sequence)

# Processing path: optional change -> mandatory verification -> outcome
process_path = gen.partial_order(dependencies=[(opt_change, code_ok), (code_ok, post_code_ok)])

# Main choice after NEW: either delete or execute the controlled processing path
main_choice = gen.xor(delete, process_path)

# Sequence: NEW -> main choice
final_model = gen.partial_order(dependencies=[(new, main_choice)])