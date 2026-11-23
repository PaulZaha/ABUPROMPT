
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# subprocess 0 changed to a loop for assessing necessity
subprocess_0 = gen.loop(change_diagn, None)

# subprocess_1 refined to ensure release happens before code_ok
subprocess_1 = gen.partial_order(dependencies = [(release, code_ok)])

# subprocess_2 changed to a loop to ensure proper billing
subprocess_2 = gen.loop(billed, None)

# subprocess_3 ensuring subprocess_1 completion before proceeding
subprocess_3 = gen.xor(subprocess_1, None)

# subprocess_4 modified to ensure accurate completion before 'FIN'
subprocess_4 = gen.partial_order(dependencies = [(subprocess_3, fin)])

# subprocess_5 to ensure proper flow and dependency check
subprocess_5 = gen.partial_order(dependencies = [(subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])

# subprocess_6 restructured to reduce unnecessary deletion
subprocess_6 = gen.xor(subprocess_5, None, delete)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])
