
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

# Activities
er_registration = gen.activity('ER Registration')
er_triage = gen.activity('ER Triage')
er_sepsis_triage = gen.activity('ER Sepsis Triage')
leucocytes = gen.activity('Leucocytes')
crp = gen.activity('CRP')
lacticacid = gen.activity('LacticAcid')
iv_liquid = gen.activity('IV Liquid')
iv_antibiotics = gen.activity('IV Antibiotics')

# Improved subprocess steps
# Make lacticacid test mandatory instead of optional to ensure accurate sepsis diagnosis
subprocess_0 = gen.activity('LacticAcid')  # Changed from xor(None, lacticacid) to ensure lacticacid test is always done

# Improved order for treatments after test results
# Ensure that IV treatments are always done after necessary tests
subprocess_1 = gen.partial_order(dependencies = [(leucocytes,), (crp,), (subprocess_0,), (iv_liquid, iv_antibiotics)])

# Remove unnecessary optional subprocess to fix wrong treatments
subprocess_4 = gen.partial_order(dependencies = [(subprocess_1,)])

# Combine triage steps and ensure sepsis triage and testing are conducted without optional detours 
final_model = gen.partial_order(dependencies = [(er_registration, er_triage), (er_triage, er_sepsis_triage), (er_sepsis_triage, subprocess_4)])
