from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
release_check = gen.activity('RELEASE & CODE OK')
close_bill = gen.activity('FIN & BILLED')

# Targeted rework loop: perform RELEASE & CODE OK once; if a diagnosis change occurs, repeat.
vr_loop = gen.loop(release_check, change_diagn)

# Optional release/check block (skip when not required)
option_release = gen.xor(None, vr_loop)

# After optional release/check, close and bill in one consolidated step
processing = gen.partial_order(dependencies=[(option_release, close_bill)])

# Early exit choices after NEW: skip, DELETE, or proceed with processing
decision = gen.xor(None, delete, processing)

final_model = gen.partial_order(dependencies=[(new, decision)])