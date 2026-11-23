
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Simplified subprocess_0 and subprocess_3
optimized_change_diagn = gen.xor(change_diagn, None)
optimized_release_code_check = gen.partial_order(dependencies = [(release,), (code_ok,)])
optimized_fin_and_release_code_check = gen.partial_order(dependencies = [(fin, optimized_release_code_check)])

# Streamlined subprocess_5 into a single partial order
optimized_billed_check = gen.xor(billed, None)
combined_process = gen.partial_order(dependencies=[(optimized_change_diagn, optimized_fin_and_release_code_check), (optimized_fin_and_release_code_check, optimized_billed_check)])

# Simplified subprocess_6 without redundant checks
final_process_path = gen.xor(delete, combined_process)

# Complete final model
final_model = gen.partial_order(dependencies = [(new, final_process_path)])
