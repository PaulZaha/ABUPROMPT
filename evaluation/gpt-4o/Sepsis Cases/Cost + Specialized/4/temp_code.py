
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Ensure Lactic Acid test is performed for any risk of sepsis by removing the XOR skip choice.
subprocess_0 = lacticacid  
# Improve efficiency by making IV Liquid and IV Antibiotics concurrent tasks.
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid,), (iv_antibiotics,)])
subprocess_2 = gen.partial_order(dependencies = [(leucocytes,), (crp,), (subprocess_0,)])
subprocess_3 = gen.xor(None, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_3)])
subprocess_5 = gen.xor(None, subprocess_4)

# Maintains overall order but integrates the optimizations made.
final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_5)]) 
