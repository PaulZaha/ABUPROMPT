
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Streamlining subprocess_1 by enforcing 'release' and 'code_ok' to execute in sequence.
subprocess_1 = gen.partial_order(dependencies=[(release, code_ok)])

# Merge subprocess_2 and subprocess_3 into a single subprocess with clearer dependencies
subprocess_2 = gen.partial_order(dependencies=[(billed, subprocess_1)])

# Simplifying subprocess_5 without the xor decision-making structure
subprocess_5 = gen.partial_order(dependencies=[(change_diagn, fin), (fin, subprocess_2)])

# Utilizing a simple structure for subprocess_6 since delete option is independent now
subprocess_6 = gen.xor(delete, subprocess_5)

final_model = gen.partial_order(dependencies=[(new, subprocess_6)])