from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Make individually optional steps to maximize useful parallelism
change_diagn_opt = gen.xor(None, change_diagn)
release_opt = gen.xor(None, release)
code_ok_opt = gen.xor(None, code_ok)
billed_opt = gen.xor(None, billed)

# Core processing path: run change, release, coding, and finalization in parallel.
# Enable billing as soon as the coding decision has been made (no need to wait for FIN).
process_path = gen.partial_order(dependencies=[
    (fin,),
    (change_diagn_opt,),
    (release_opt,),
    (code_ok_opt,),
    (code_ok_opt, billed_opt)
])

# After NEW, choose to DELETE, proceed with processing, or skip.
process_choice = gen.xor(None, delete, process_path)

# Ensure NEW precedes the choice, improving feasibility while preserving overall speed via internal parallelization.
final_model = gen.partial_order(dependencies=[(new, process_choice)])