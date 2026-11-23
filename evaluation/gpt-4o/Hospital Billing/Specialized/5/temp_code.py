
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Improvement: Make diagnosis mandatory
subprocess_0 = change_diagn 

# Improvement: Add dependency between release and code_ok
subprocess_1 = gen.partial_order(dependencies = [(release, code_ok)])

# Improvement: Make billed mandatory
subprocess_2 = billed 

subprocess_3 = subprocess_1 # Removed optionality, subprocess_1 must happen

subprocess_4 = gen.partial_order(dependencies = [(fin,), (subprocess_3,)])
subprocess_5 = gen.partial_order(dependencies = [(subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])
subprocess_6 = gen.xor(None, delete, subprocess_5)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])
