
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

# Simplifying the lactic acid inclusion based on a medical protocol
subprocess_0 = lacticacid  # Removed optional nature, assuming it's critical
subprocess_1 = gen.partial_order(dependencies = [(iv_liquid, iv_antibiotics)])  # Based on critical concurrent requirement or potential protocol check

# Streamlined decision path for tests
subprocess_2 = gen.partial_order(dependencies = [(leucocytes,), (crp,), (subprocess_0,)])
subprocess_4 = gen.partial_order(dependencies = [(subprocess_2, subprocess_1)])  # Removed optional nature of combined protocol tests

final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_4)])  # Integrated necessary paths only
