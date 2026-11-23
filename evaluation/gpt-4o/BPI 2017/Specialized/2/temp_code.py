
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

# New activities for notifications
notify_application_received = gen.activity('Notify Application Received')
notify_concept_generated = gen.activity('Notify Concept Generated')
notify_offers_sent = gen.activity('Notify Offers Sent')

subprocess_0 = gen.loop(w_handle_leads, None)
subprocess_1 = gen.loop(w_complete_application, None)
subprocess_2 = gen.xor(None, a_concept)
subprocess_3 = gen.partial_order(dependencies = [(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online), (o_sent_mail_and_online, notify_offers_sent)])
subprocess_4 = gen.loop(w_call_after_offers, None)
subprocess_5 = gen.partial_order(dependencies = [(a_cancelled, o_cancelled)])
subprocess_6 = gen.partial_order(dependencies = [(a_submitted, notify_application_received), (notify_application_received, subprocess_0)])
subprocess_7 = gen.xor(None, subprocess_3, notify_concept_generated)
subprocess_8 = gen.xor(a_complete, subprocess_5)
subprocess_9 = gen.xor(None, subprocess_6)
subprocess_10 = gen.partial_order(dependencies = [(subprocess_2, subprocess_7)])
subprocess_11 = gen.loop(subprocess_4, subprocess_8)
subprocess_12 = gen.loop(subprocess_1, subprocess_10)

final_model = gen.partial_order(dependencies = [(a_create_application, subprocess_9), (subprocess_9, subprocess_12), (subprocess_12, subprocess_11)])
