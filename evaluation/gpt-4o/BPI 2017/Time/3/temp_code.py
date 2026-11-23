
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
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')
a_complete = gen.activity('A_Complete')
w_call_after_offers = gen.activity('W_Call after offers')

# Consolidate subprocess_1: Complete application takes place only once
subprocess_complete_application = gen.xor(None, w_complete_application)

# Remove redundant loop in subprocess_0: Handle leads in sequence
subprocess_handle_leads = gen.xor(None, w_handle_leads)

# Rework subprocesses with concurrency and remove loops
subprocess_concept_accepted = gen.partial_order(dependencies=[(a_concept, a_accepted)])
subprocess_offer_creation = gen.partial_order(dependencies=[(o_create_offer, o_created, o_sent_mail_and_online)])

# Combine processes and allow concurrency where possible
subprocess_offer_process = gen.partial_order(dependencies=[(subprocess_concept_accepted, subprocess_offer_creation)])

subprocess_call_and_complete = gen.partial_order(dependencies=[(w_call_after_offers, a_complete)])
subprocess_cancellation = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Simplify subprocess handling with concurrency
subprocess_creation = gen.partial_order(dependencies=[(a_submitted, subprocess_handle_leads)])

final_model = gen.partial_order(dependencies=[
    (a_create_application, subprocess_creation), 
    (subprocess_creation, subprocess_complete_application), 
    (subprocess_complete_application, subprocess_offer_process), 
    (subprocess_offer_process, subprocess_call_and_complete), 
    (subprocess_call_and_complete, subprocess_cancellation)
])
