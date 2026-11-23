
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# 'CHANGE DIAGN' as mandatory step based on concrete rules
subprocess_0 = change_diagn

# 'RELEASE', 'CODE OK' should be concurrent, not optional
subprocess_1 = gen.partial_order(dependencies = [(release, code_ok)])
subprocess_1_concurrent = gen.partial_order(dependencies = [(subprocess_1,)])

# Making subprocess_1 mandatory rather than optional
subprocess_2 = gen.xor(delete, subprocess_1_concurrent)

# Making 'billed' as a continuing necessary step
subprocess_3 = billed 

# Increase concurrency for subprocess_1
subprocess_4 = gen.partial_order(dependencies = [(fin, subprocess_2, subprocess_3)])

# Improved structure reducing optionality
final_model = gen.partial_order(dependencies = [(new, subprocess_4)])
