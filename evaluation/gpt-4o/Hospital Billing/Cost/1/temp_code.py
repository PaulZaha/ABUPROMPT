
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Enhance parallelism and remove non-essential sequences
subprocess_0 = gen.partial_order(dependencies = [(change_diagn,)])
subprocess_1 = gen.partial_order(dependencies = [(release, code_ok)]) 
subprocess_2 = gen.xor(None, billed)
subprocess_3 = gen.xor(delete, subprocess_1, subprocess_2) # combining subprocess 1 and subprocess 5 parallelism
subprocess_4 = gen.partial_order(dependencies = [(subprocess_3, fin)]) # reducing optional steps and enhancing concurrency
subprocess_5 = gen.xor(subprocess_0, subprocess_4)

final_model = gen.partial_order(dependencies = [(new, subprocess_5)]) # optimized parallel execution post-process validation
