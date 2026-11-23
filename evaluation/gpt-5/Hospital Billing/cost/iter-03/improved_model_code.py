from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Optional early correction to prevent downstream rework
opt_change = gen.xor(None, change_diagn)

# Billing branch: only executed when billing is needed
# Ensures RELEASE -> FIN -> BILLED
bill_path = gen.partial_order(dependencies=[(release, fin), (fin, billed)])

# No-billing branch: finalize directly (separate instance of FIN)
fin_no_bill = fin.copy()

# Decide whether to bill after the quality gate (CODE OK)
branch_after_code_ok = gen.xor(bill_path, fin_no_bill)

# Core processing: optional CHANGE DIAGN -> CODE OK -> (bill or no-bill branch)
core = gen.partial_order(dependencies=[(opt_change, code_ok), (code_ok, branch_after_code_ok)])

# After NEW, either delete or execute the core processing (no more do-nothing path)
post_new_choice = gen.xor(delete, core)

final_model = gen.partial_order(dependencies=[(new, post_new_choice)])