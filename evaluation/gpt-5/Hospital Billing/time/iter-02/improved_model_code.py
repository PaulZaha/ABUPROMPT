from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Optional steps
opt_change = gen.xor(None, change_diagn)
opt_release = gen.xor(None, release)
opt_code = gen.xor(None, code_ok)
opt_billed = gen.xor(None, billed)

# Main flow with maximized concurrency and minimal prerequisites
main_flow = gen.partial_order(dependencies=[
    (opt_release,),           # RELEASE can proceed independently
    (fin,),                   # FIN can start immediately
    (opt_change, opt_code),   # CODE OK waits for CHANGE DIAGN (if it happens)
    (opt_code, opt_billed),   # BILLED after CODE OK (if executed)
    (fin, opt_billed)         # and after FIN
])

# After NEW: choose to DELETE, do nothing, or execute main flow
post_new = gen.xor(None, delete, main_flow)

final_model = gen.partial_order(dependencies=[(new, post_new)])