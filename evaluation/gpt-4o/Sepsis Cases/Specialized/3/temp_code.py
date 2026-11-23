
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

# Lactic Acid test should be mandatory for better assessment 
subprocess_0 = gen.partial_order(dependencies=[(lacticacid,)])

# The treatment following diagnostics is compulsory and follows a specific sequence
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])
subprocess_2 = gen.partial_order(dependencies = [(leucocytes, crp, subprocess_0)])

# Remove optionality for the subprocess_3 to make vital treatment tests compulsory
subprocess_3 = subprocess_1

subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_3)])

# Improve sequence by ensuring diagnostics are completed before treatment.
final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_4)])
