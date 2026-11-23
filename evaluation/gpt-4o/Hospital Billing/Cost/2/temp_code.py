
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Combine subprocess_0 and subprocess_4 into a sequence as they seem to be check processes 
subprocess_seq = gen.partial_order(dependencies = [(change_diagn,), (release, code_ok), (fin,)])

# Simplify subprocess_5 by removing redundant choices and combining subprocesses
subprocess_5 = gen.partial_order(dependencies = [(subprocess_seq, billed)])

# Simplify subprocess_6 by removing optional structure for change_diagn
subprocess_6 = gen.xor(delete, subprocess_5)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])
