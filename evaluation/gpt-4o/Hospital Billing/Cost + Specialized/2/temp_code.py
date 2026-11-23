
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
subprocess_1 = gen.partial_order(dependencies = [(release, code_ok)])  # Making release and code_ok mandatory
subprocess_2 = billed  # Making billed mandatory after subprocess_1
subprocess_3 = subprocess_1  # Removing optionality
subprocess_4 = gen.partial_order(dependencies = [(fin, subprocess_3)])  # Linear flow for finalization
subprocess_5 = gen.partial_order(dependencies = [(subprocess_0, subprocess_4), (subprocess_4, subprocess_2)])  # Billing path enhanced
subprocess_6 = gen.xor(delete, subprocess_5)  # Removing optionality making it a clear choice

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])  # Keeping NEW as starting
