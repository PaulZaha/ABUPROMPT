
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

subprocess_0 = gen.xor(None, change_diagn)
subprocess_1 = gen.partial_order(dependencies=[(release, code_ok)])
subprocess_2 = gen.xor(None, billed)
subprocess_4 = gen.partial_order(dependencies=[(fin,), (subprocess_1,)])
subprocess_5 = gen.partial_order(dependencies=[(subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])

final_model = gen.partial_order(dependencies=[(new, subprocess_5)])
