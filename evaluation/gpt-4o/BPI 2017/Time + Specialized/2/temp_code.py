
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
notify_customer_application = gen.activity('Notify Customer Application Status')
notify_customer_offer = gen.activity('Notify Customer Offer')

# Subprocess adjustments to optimize flow
subprocess_0 = gen.partial_order(dependencies=[(w_handle_leads, a_submitted)])  # Eliminated unnecessary looping
subprocess_1 = gen.partial_order(dependencies=[(w_complete_application, notify_customer_application)])  # Ensure customer is informed post-application completion
subprocess_2 = gen.xor(None, a_concept)
subprocess_3 = gen.partial_order(dependencies=[(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online), (o_sent_mail_and_online, notify_customer_offer)])  # Inform customer after offer
subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
subprocess_7 = gen.xor(None, subprocess_3)
subprocess_8 = gen.xor(a_complete, subprocess_5)

# Optimize subprocesses by allowing concurrency
concurrent_creation_notify = gen.partial_order(dependencies=[(subprocess_2,), (subprocess_7,)])

final_model = gen.partial_order(dependencies=[
    (a_create_application, subprocess_0),
    (subprocess_0, subprocess_1),
    (subprocess_1, concurrent_creation_notify),
    (concurrent_creation_notify, gen.loop(w_call_after_offers, subprocess_8))
])
