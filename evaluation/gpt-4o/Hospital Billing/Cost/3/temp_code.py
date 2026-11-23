
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
fin = gen.activity('FIN')
billed = gen.activity('BILLED')

# Simplify subprocess_0: remove optional 'CHANGE DIAGN'.
subprocess_1 = gen.partial_order(dependencies = [(release,), (code_ok,)])

# Ensure 'BILLED' is essential post-processing.
subprocess_2 = gen.partial_order(dependencies = [(billed,)])

# Integrate subprocess_1 directly into process.
subprocess_4 = gen.partial_order(dependencies = [(fin,), (subprocess_1,)])

# Restructure to remove optional behavior.
subprocess_5 = gen.partial_order(dependencies = [(subprocess_4,), (subprocess_4, subprocess_2)])
subprocess_6 = gen.xor(delete, subprocess_5)  # Ensure value or criteria-defined choice.

# Final model with efficient reduced execution paths.
final_model = gen.partial_order(dependencies = [(new, subprocess_6)])
