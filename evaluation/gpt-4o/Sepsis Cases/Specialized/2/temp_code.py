
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

# Ensure LacticAcid is mandatory for suspected sepsis triage.
subprocess_0 = gen.partial_order(dependencies=[(lacticacid,)])

# Modify subprocess_2 to ensure Leucocytes, CRP tests are mandatory:
subprocess_2 = gen.partial_order(dependencies=[(leucocytes, crp, subprocess_0)])

# add checks to ensure appropriate use of IV medications based on test results
subprocess_1 = gen.xor(iv_liquid, iv_antibiotics)

# Link subprocess_4 with mandatory test results prior to treatment decisions.
subprocess_3 = gen.partial_order(dependencies=[(subprocess_2, subprocess_1)])

final_model = gen.partial_order(dependencies=[(er_registration, er_triage), 
                                                (er_triage, er_sepsis_triage), 
                                                (er_sepsis_triage, subprocess_3)])
