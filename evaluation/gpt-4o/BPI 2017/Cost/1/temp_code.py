
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

# Remove excessive loops by consolidating or ensuring efficient execution
subprocess_0 = w_handle_leads  # Removed self-loop
subprocess_1 = w_complete_application  # Removed self-loop
subprocess_4 = w_call_after_offers  # Removed self-loop

# Optional subprocesses streamlined
subprocess_6 = a_submitted  # Directly connect without loop
subprocess_2 = gen.xor(None, a_concept)  # Retained for necessary optionality
subprocess_9 = subprocess_6  # Simplified subprocess_9 by direct connection

# Enhance concurrency
subprocess_3 = gen.partial_order(dependencies=[(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])

subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
subprocess_7 = gen.xor(None, subprocess_3)
subprocess_8 = gen.xor(a_complete, subprocess_5)

# Self-loop elimination 
subprocess_10 = gen.partial_order(dependencies=[(subprocess_2, subprocess_7)])
subprocess_12 = gen.partial_order(dependencies=[(subprocess_1, subprocess_10)])  # Removed loop

# Combine processes to improve concurrency
final_model = gen.partial_order(dependencies=[
    (a_create_application, subprocess_9),
    (subprocess_9, subprocess_12),
    (subprocess_12, subprocess_4, subprocess_8)  # Consolidated processes for increased concurrency
])
