
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

# Ensuring concurrent execution of lab tests simultaneously
subprocess_2 = gen.partial_order(dependencies = [(leucocytes, crp, lacticacid)]) 

# Streamlining IV treatments to be concurrent
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])

# Modifying subprocess_4 to remove optional execution
subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_1)])

# Removing subprocess_5 as optional, direct integration into the final model
final_model = gen.partial_order(dependencies=[
    (er_registration, er_triage), 
    (er_triage, er_sepsis_triage), 
    (er_sepsis_triage, subprocess_4)
])
