
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

# Removed unnecessary self-loop around 'W_Handle leads'
subprocess_0 = w_handle_leads

# Removed redundant self-loop around 'W_Complete application'
subprocess_1 = w_complete_application

# Optimized XOR by making 'A_Concept' optional, removing redundant components
subprocess_2 = gen.xor(None, a_concept)

subprocess_3 = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer), 
    (o_create_offer, o_created), 
    (o_created, o_sent_mail_and_online)
])

# Removed unnecessary self-loop around 'W_Call after offers'
subprocess_4 = w_call_after_offers

subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Direct sequential dependency since self-loop removed from subprocess_0
subprocess_6 = gen.partial_order(dependencies=[(a_submitted, subprocess_0)])

# XOR operation cleaned up, subprocess_3 kept optional 
subprocess_7 = gen.xor(None, subprocess_3)

subprocess_8 = gen.xor(a_complete, subprocess_5)

# XOR operation cleaned up for subprocess_6
subprocess_9 = gen.xor(None, subprocess_6)

subprocess_10 = gen.partial_order(dependencies=[(subprocess_2, subprocess_7)])

# Dependencies consolidated, removed self-looping redo parts
subprocess_11 = gen.partial_order(dependencies=[
    (subprocess_4, subprocess_8)
])

subprocess_12 = gen.partial_order(dependencies=[
    (subprocess_1, subprocess_10)
])

# Final model adjusted to remove redundant cycles and delays
final_model = gen.partial_order(dependencies=[
    (a_create_application, subprocess_9), 
    (subprocess_9, subprocess_12), 
    (subprocess_12, subprocess_11)
])
