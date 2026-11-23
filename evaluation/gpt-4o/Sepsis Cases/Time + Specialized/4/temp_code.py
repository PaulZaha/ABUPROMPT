
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

# Modify subprocess_0 to remove optional lacticacid test
subprocess_0 = lacticacid

# Modify subprocess_2 to make tests concurrent
subprocess_2 = gen.partial_order(dependencies = [(leucocytes, crp, subprocess_0)])

# Feedback loop around subprocess_4
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])
subprocess_3 = gen.xor(None, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_3)])
feedback_loop = gen.loop(subprocess_4, None)

# Update final model to include feedback loop
final_model = gen.partial_order(dependencies = [(er_registration, er_triage),
                                                (er_triage, er_sepsis_triage),
                                                (er_sepsis_triage, feedback_loop)])
