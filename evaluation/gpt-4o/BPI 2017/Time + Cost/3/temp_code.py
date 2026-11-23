
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

a_create_application = gen.activity('A_Create Application')
a_submitted = gen.activity('A_Submitted')
w_handle_leads = gen.activity('W_Handle leads')
w_complete_application = gen.activity('W_Complete application')
a_concept = gen.activity('A_Concept')
a_accepted = gen.activity('A_Accepted')
o_create_offer = gen.activity('O_Create Offer')
o_created = gen.activity('O_Created')
o_sent_mail_and_online = gen.activity('O_Sent (mail and online)')
w_call_after_offers = gen.activity('W_Call after offers')
a_complete = gen.activity('A_Complete')
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')

subprocess_0 = gen.partial_order(dependencies=[(w_handle_leads,), (w_complete_application,)])  # Parallelization
subprocess_1 = gen.xor(None, a_concept)
subprocess_2 = gen.partial_order(dependencies = [(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)]) # Simplified direct order
subprocess_3 = gen.partial_order(dependencies = [(a_cancelled, o_cancelled)])
subprocess_4 = gen.partial_order(dependencies = [(a_submitted, subprocess_0)])  # Mandatory subprocess
subprocess_5 = gen.partial_order(dependencies = [(a_complete, subprocess_3)])  # Enforced completion
subprocess_6 = gen.partial_order(dependencies = [(subprocess_1, subprocess_2)])  # Combined concept and offer creation
subprocess_7 = gen.loop(w_call_after_offers, subprocess_5)  # Reduced looping
subprocess_8 = gen.partial_order(dependencies = [(subprocess_4, subprocess_6)])  # Unified subprocesses
subprocess_9 = gen.partial_order(dependencies = [(subprocess_8, subprocess_7)])  # Streamlined main process flow

final_model = gen.partial_order(dependencies = [(a_create_application, subprocess_9)])
