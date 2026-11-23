
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

# New activities for customer communication
notify_customer_application_submitted = gen.activity('Notify Customer of Application Submission')
notify_customer_concept_complete = gen.activity('Notify Customer of Concept Completion')
notify_customer_offer_created = gen.activity('Notify Customer Offer Created')
notify_customer_offer_sent = gen.activity('Notify Customer Offer Sent')
notify_customer_application_complete = gen.activity('Notify Customer Application Completion')
notify_customer_cancelled = gen.activity('Notify Customer of Cancellation')

subprocess_0 = gen.loop(w_handle_leads, None)
subprocess_1 = gen.loop(w_complete_application, None)
subprocess_2 = gen.xor(None, a_concept)

# Modified subprocess to include customer notification after concept is completed
subprocess_3 = gen.partial_order(dependencies = [(a_accepted, notify_customer_concept_complete), (notify_customer_concept_complete, o_create_offer), (o_create_offer, notify_customer_offer_created), (notify_customer_offer_created, o_created), (o_created, o_sent_mail_and_online), (o_sent_mail_and_online, notify_customer_offer_sent)])

subprocess_4 = gen.loop(w_call_after_offers, None)
subprocess_5 = gen.partial_order(dependencies = [(a_cancelled, notify_customer_cancelled), (notify_customer_cancelled, o_cancelled)])
subprocess_6 = gen.partial_order(dependencies = [(a_submitted, notify_customer_application_submitted), (notify_customer_application_submitted, subprocess_0)])
subprocess_7 = gen.xor(None, subprocess_3)
subprocess_8 = gen.xor(a_complete, notify_customer_application_complete, subprocess_5)

subprocess_9 = gen.xor(None, subprocess_6)
subprocess_10 = gen.partial_order(dependencies = [(subprocess_2, subprocess_7)])
subprocess_11 = gen.loop(subprocess_4, subprocess_8)
subprocess_12 = gen.loop(subprocess_1, subprocess_10)

final_model = gen.partial_order(dependencies = [(a_create_application, subprocess_9), (subprocess_9, subprocess_12), (subprocess_12, subprocess_11)])