from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Rework loop: perform CODE OK; if changes are needed, execute CHANGE DIAGN and re-check
code_check_loop = gen.loop(code_ok, change_diagn)

# Billing path only: code check loop -> RELEASE -> BILLED
billed_path = gen.partial_order(dependencies=[(code_check_loop, release), (release, billed)])

# After finalization, optionally proceed to billing path
post_fin_choice = gen.xor(None, billed_path)

# Core path for active (non-deleted) cases: FIN must precede any billing activities
continue_path = gen.partial_order(dependencies=[(fin, post_fin_choice)])

# After NEW, either stop, DELETE, or proceed with the process
after_new_choice = gen.xor(None, delete, continue_path)

# NEW must happen before any subsequent path
final_model = gen.partial_order(dependencies=[(new, after_new_choice)])