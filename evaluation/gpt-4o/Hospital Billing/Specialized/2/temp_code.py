
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
external_verification = gen.activity('EXTERNAL VERIFICATION')
billed = gen.activity('BILLED')

subprocess_0 = gen.xor(None, change_diagn)
subprocess_1 = gen.partial_order(dependencies=[(external_verification,), (release,)])
subprocess_2 = gen.xor(None, billed)
subprocess_3 = gen.xor(None, subprocess_1)
subprocess_4 = gen.partial_order(dependencies=[(fin,), (subprocess_3,)])
subprocess_5 = gen.partial_order(dependencies=[(subprocess_0,), (subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])
subprocess_6 = gen.xor(None, delete, subprocess_5)

final_model = gen.partial_order(dependencies=[(new,), (new, subprocess_6)])