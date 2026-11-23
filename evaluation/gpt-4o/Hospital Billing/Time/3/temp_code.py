
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Make 'CHANGE DIAGN' always execute, removing the optionality
subprocess_0 = change_diagn

# Concurrent execution of 'RELEASE' and 'CODE OK'
subprocess_1 = gen.partial_order(dependencies=[(release,), (code_ok,)])

# Removed optionality from 'BILLED'
subprocess_2 = billed

# 'FIN' must execute after completion of subprocess_1; removing optional 'subprocess_3' defined earlier
subprocess_4 = gen.partial_order(dependencies=[(subprocess_1,), (fin,)])

# Concurrency of subprocess_0 and subprocess_4
subprocess_5 = gen.partial_order(dependencies=[(subprocess_0,), (subprocess_4,), (subprocess_2,)])

# Process improved with mandatory execution paths and enhanced concurrency
subprocess_6 = gen.xor(delete, subprocess_5)

final_model = gen.partial_order(dependencies=[(new,), (subprocess_6,)]) 
