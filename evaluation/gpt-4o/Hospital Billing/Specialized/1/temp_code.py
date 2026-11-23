
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Ensure RELEASE and CODE OK are mandatory:
subprocess_0 = gen.partial_order(dependencies = [(release, code_ok)])

# Ensure CHANGE DIAGN is conditionally linked:
subprocess_1 = gen.xor(change_diagn, None)  # make CHANGE DIAGN unconditional

# Synchronize billing:
subprocess_2 = gen.partial_order(dependencies = [(fin,), (billed,)])
process_completion = gen.partial_order(dependencies = [(subprocess_0,), (subprocess_1,), (subprocess_2,)])

# Update with improved sequences:
subprocess_3 = gen.xor(None, delete, process_completion)

final_model = gen.partial_order(dependencies = [(new, subprocess_3)]) 
