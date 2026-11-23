
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Restructuring process for increased concurrency and removal of redundancies
concurrency_subprocess = gen.partial_order(dependencies=[(change_diagn,), (release,), (code_ok,), (billed,)])

subprocess_1 = gen.partial_order(dependencies = [(delete,), (concurrency_subprocess,)])
subprocess_2 = gen.partial_order(dependencies = [(fin,), (subprocess_1,)])

final_model = gen.partial_order(dependencies = [(new, subprocess_2)])
