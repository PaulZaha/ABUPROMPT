from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Individually optional steps
opt_change = gen.xor(None, change_diagn)
opt_release = gen.xor(None, release)
opt_code_ok = gen.xor(None, code_ok)
opt_billed = gen.xor(None, billed)

# Main processing branch: more concurrency; billing and QC gated by final diagnosis
process_branch = gen.partial_order(dependencies=[
    (opt_change, opt_code_ok),   # QC after final diagnosis
    (fin, opt_billed),           # bill after finalization
    (opt_code_ok, opt_billed),   # bill after QC (if executed)
    (opt_change, opt_billed),    # bill after final diagnosis (if executed)
    (opt_release, opt_billed)    # bill after release (if executed)
])

# After NEW: skip, DELETE, or execute the processing branch
post_new = gen.xor(None, delete, process_branch)

final_model = gen.partial_order(dependencies=[(new, post_new)])