
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Combine subprocess_1 and subprocess_2 to allow parallel execution where possible
subprocess_1_2 = gen.partial_order(dependencies=[(release, code_ok), (code_ok,billed)])
subprocess_fin = gen.partial_order(dependencies=[(fin, subprocess_1_2)])

# Merge subprocess_0 and subprocess_fin into an exclusive choice to reduce optional paths
subprocess_combined = gen.xor(change_diagn, subprocess_fin)

# New subprocess_6 optimization
subprocess_6 = gen.xor(delete, subprocess_combined)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])