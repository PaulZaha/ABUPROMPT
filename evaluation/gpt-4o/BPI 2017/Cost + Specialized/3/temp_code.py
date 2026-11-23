
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
w_call_after_notification = gen.activity('W_Call after notification')
a_complete = gen.activity('A_Complete')
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')

# Streamlined lead handling
subprocess_0 = gen.xor(w_handle_leads, None)

# Notification added after application completion
subprocess_1 = gen.partial_order(dependencies=[(w_complete_application, w_call_after_notification)])

# Mandatory concept acceptance process
subprocess_2 = gen.partial_order(dependencies=[(a_concept, a_accepted)])

# Optimized offer creation and communication
subprocess_3 = gen.partial_order(dependencies=[(o_create_offer, o_sent_mail_and_online)])

# Direct conclusion without repetitive calls
subprocess_4 = gen.xor(a_complete, subprocess_3)

# Simplified cancellation pathway
subprocess_5 = gen.xor(a_cancelled, o_cancelled)

subprocess_6 = gen.partial_order(dependencies=[(a_submitted, subprocess_0)])
subprocess_7 = gen.partial_order(dependencies=[(subprocess_2, subprocess_4)])
subprocess_8 = gen.xor(None, subprocess_6)
subprocess_9 = gen.partial_order(dependencies=[(subprocess_8, subprocess_1), (subprocess_1, subprocess_7)])

final_model = gen.partial_order(dependencies=[(a_create_application, subprocess_9), (subprocess_9, subprocess_5)])
