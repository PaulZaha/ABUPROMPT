
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

# New activities for customer information and efficiency
inform_submission = gen.activity('Inform Customer of Submission')
inform_offer_creation = gen.activity('Inform Customer Offer Created')

# Process Elements / Subprocess
subprocess_0 = gen.loop(w_handle_leads, None)
subprocess_1 = gen.loop(w_complete_application, None)

# Concurrent processing combo - Application and Inform Customer are now concurrent
subprocess_2 = gen.partial_order(dependencies = [(a_submitted, inform_submission), (inform_submission,), (subprocess_0,)])

subprocess_3 = gen.xor(None, a_concept)

# Partial order for offer creation now includes informing customer
subprocess_4 = gen.partial_order(dependencies = [(a_accepted, o_create_offer), (o_create_offer, inform_offer_creation), (inform_offer_creation, o_created), (o_created, o_sent_mail_and_online)])

subprocess_5 = gen.loop(w_call_after_offers, None)
subprocess_6 = gen.partial_order(dependencies = [(a_cancelled, o_cancelled)])

# New concurrency and sequence updates
subprocess_7 = gen.partial_order(dependencies=[(a_create_application, subprocess_2), (subprocess_2, subprocess_3)])
subprocess_8 = gen.xor(None, subprocess_4)
subprocess_9 = gen.loop(subprocess_5, subprocess_6)

final_model = gen.partial_order(dependencies = [(subprocess_7, subprocess_8), (subprocess_8, subprocess_9)])