
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Introducing a quality check activity for improved external quality
quality_check = gen.activity('QUALITY CHECK')

subprocess_0 = gen.xor(None, change_diagn)
# Allow release and code_ok to execute concurrently
subprocess_1 = gen.partial_order(dependencies = [(release, code_ok)])
subprocess_2 = gen.xor(None, billed)
subprocess_3 = gen.xor(None, subprocess_1)
# Allow fin and subprocess_3 to execute concurrently
subprocess_4 = gen.partial_order(dependencies = [(fin, subprocess_3)])
# Simplification and quality assurance check added before subprocess_0
subprocess_5 = gen.partial_order(dependencies = [(quality_check, subprocess_0), (subprocess_4, subprocess_2)])
# Simplified to focus decision-making around essential check and process completion
subprocess_6 = gen.xor(delete, subprocess_5)

final_model = gen.partial_order(dependencies = [(new, subprocess_6)])