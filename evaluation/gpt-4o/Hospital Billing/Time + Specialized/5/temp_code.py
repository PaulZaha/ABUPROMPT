
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

# Existing activities
new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Modified subprocesses to simplify and improve execution time and external quality
subprocess_0_modified = change_diagn # Make the change_diagn mandatory, assuming it's critical for quality
subprocess_1_modified = gen.partial_order(dependencies=[(release,), (code_ok,)]) # Allow concurrent execution
subprocess_2_modified = billed # Make billing a required activity and ensure quality
subprocess_4_modified = gen.partial_order(dependencies=[(fin, subprocess_1_modified)]) # Simplify subprocess without optional path

# Combine subprocess_0 and subprocess_4, removing decision points
subprocess_combined = gen.partial_order(dependencies=[(subprocess_0_modified,), (subprocess_4_modified,)])
subprocess_5_modified = gen.partial_order(dependencies=[(subprocess_combined, subprocess_2_modified)])

# Final subprocess holding delete and consolidated path
subprocess_6_modified = gen.xor(delete, subprocess_5_modified) # Removed unnecessary optional path

# Final model integrating improvements
final_model = gen.partial_order(dependencies=[(new, subprocess_6_modified)])
