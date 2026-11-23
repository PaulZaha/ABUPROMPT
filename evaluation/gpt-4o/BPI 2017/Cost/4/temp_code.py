
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

# Activities
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

# Avoid unnecessary loops and make subprocess_0 optional to streamline handling leads
subprocess_0 = gen.xor(w_handle_leads, None)
subprocess_1 = gen.xor(w_complete_application, None)

# Keeping conceptual model optional, simplifying choices
subprocess_2 = gen.xor(None, a_concept)
subprocess_3 = gen.partial_order(dependencies = [(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])

# Streamlined offer follow up; potentially repetitively done once at max
subprocess_4 = gen.xor(w_call_after_offers, None)
subprocess_5 = gen.partial_order(dependencies = [(a_cancelled, o_cancelled)])
subprocess_6 = gen.xor(a_submitted, None)

# Ensuring offer creation and submission clearly delineated without loops
subprocess_7 = gen.xor(None, subprocess_3)
subprocess_8 = gen.xor(a_complete, subprocess_5)

# Transformed optional lead handling
subprocess_9 = gen.partial_order(dependencies=[(subprocess_6, subprocess_0)])
subprocess_10 = gen.partial_order(dependencies=[(subprocess_2, subprocess_7)])
subprocess_11 = gen.partial_order(dependencies=[(subprocess_4, subprocess_8)])
subprocess_12 = gen.partial_order(dependencies=[(subprocess_1, subprocess_10)])

# Updated final model
final_model = gen.partial_order(dependencies = [(a_create_application, subprocess_9), (subprocess_9, subprocess_12), (subprocess_12, subprocess_11)]) 
