
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Removing the optionality for subprocess_0 and subprocess_1 in subprocess_5 to streamline execution
subprocess_1 = gen.partial_order(dependencies = [(release,), (code_ok,)])

# Optimizing concurrency and eliminating repetitive optional subprocess_3 by incorporating subprocess_1 directly
subprocess_4 = gen.partial_order(dependencies = [(fin,), (subprocess_1,)])
subprocess_5 = gen.partial_order(dependencies = [(change_diagn, subprocess_4), (subprocess_4, billed)])
subprocess_6 = gen.xor(None, delete, subprocess_5)

# Final model maximizing the concurrency during new and subprocess_6
final_model = gen.partial_order(dependencies = [(new, subprocess_6)])
