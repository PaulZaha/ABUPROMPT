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

# Allow 0..n diagnosis changes
change_loop = gen.loop(None, change_diagn)

# Each change cycle must end with a validation
validation_pair = gen.partial_order(dependencies=[(change_loop, code_ok)])

# Permit repeating the (changes -> validation) pair from 1..n times
validation_cycle = gen.loop(validation_pair, None)

# Billing is optional but only after release
billing_optional = gen.xor(None, billed)

# Quality-assured normal flow
normal_flow = gen.partial_order(dependencies=[(validation_cycle, fin), (fin, release), (release, billing_optional)])

# After NEW, explicitly choose to DELETE or proceed (no silent skip)
decision = gen.xor(delete, normal_flow)

final_model = gen.partial_order(dependencies=[(new, decision)])