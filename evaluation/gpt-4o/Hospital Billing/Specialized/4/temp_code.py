
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

subprocess_0 = gen.xor(None, change_diagn)  # allowing a diagnostic change as non-mandatory
subprocess_1 = gen.partial_order(dependencies = [(release,), (code_ok,)])  # ensuring quality checks are done
subprocess_2 = billed  # billing becomes a mandatory step
subprocess_3 = subprocess_1.copy()  # ensuring subprocess_1 is checked for each path
subprocess_4 = gen.partial_order(dependencies = [(subprocess_3, fin)])  # 'FIN' follows subprocess_3 completion
subprocess_5 = gen.partial_order(dependencies = [(subprocess_4, subprocess_0), (subprocess_0, subprocess_2)])
subprocess_6 = gen.xor(None, delete, subprocess_5)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])