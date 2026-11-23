
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

# Change subprocess_1 from sequence to concurrent execution 
subprocess_1 = gen.partial_order(dependencies=[(release,), (code_ok,)])

subprocess_2 = gen.xor(None, billed)

# Remove the optional structure for subprocess_3 to ensure subprocess_1 is always executed
subprocess_4 = gen.partial_order(dependencies=[(fin,), (subprocess_1,)])

subprocess_5 = gen.partial_order(dependencies=[(subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])

# Remove delete as optional in subprocess_6 to streamline process
subprocess_6 = gen.xor(delete, subprocess_5)

# Final model remains similar but with improved subprocess handling
final_model = gen.partial_order(dependencies=[(new, subprocess_6)])
