
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Removing subprocess_0 as it may unnecessarily add to cost without improving quality
# subprocess_0 = gen.xor(None, change_diagn)    
               
# Instead of subprocess_3, we simplify subprocess_1 
subprocess_1 = gen.partial_order(dependencies = [(release,), (code_ok,)])
# Making billed mandatory to improve external quality
subprocess_2 = gen.partial_order(dependencies=[(billed,)])
subprocess_4 = gen.partial_order(dependencies = [(fin,), (subprocess_1,)])
subprocess_5 = gen.partial_order(dependencies = [(subprocess_4, subprocess_2)])
subprocess_6 = gen.xor(delete, subprocess_5)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])