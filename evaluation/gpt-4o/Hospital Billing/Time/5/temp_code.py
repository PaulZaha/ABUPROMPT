
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Remove unnecessary XOR for subprocess_3 to make subprocess_1 always execute
subprocess_0 = gen.xor(None, change_diagn)

# Enhance concurrency between 'release' and 'code_ok'
subprocess_1 = gen.partial_order(dependencies=[(release,), (code_ok,)])

# Ensure subprocess_2 is optional for billing
subprocess_2 = gen.xor(None, billed)

# Simplify subprocess_4 to ensure FIN is simultaneously possible with subprocess_1
subprocess_4 = gen.partial_order(dependencies=[(fin,), (subprocess_1,)])

# Refine subprocess_5 to eliminate decision redundancy and improve flow
subprocess_5 = gen.partial_order(dependencies=[(subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])

# Streamline subprocess_6 with better alignment between DELETE and subprocess_5
subprocess_6 = gen.xor(None, delete, subprocess_5)

# Construct the final model with the improved subprocess arrangements
final_model = gen.partial_order(dependencies=[(new, subprocess_6)])
