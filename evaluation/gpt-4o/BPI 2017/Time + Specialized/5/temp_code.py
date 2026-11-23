
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

# New activities to keep customer informed
notify_submitted = gen.activity('Notify Submitted')
notify_offer_created = gen.activity('Notify Offer Created')
notify_complete = gen.activity('Notify Complete')
notify_cancelled = gen.activity('Notify Cancelled')

subprocess_0 = gen.xor(w_handle_leads, None)  # Change to optional xor to reduce repetitive loops
subprocess_1 = gen.xor(w_complete_application, None)  # Change to optional xor to reduce repetitive loops
subprocess_2 = gen.xor(None, a_concept) 
subprocess_3 = gen.partial_order(dependencies = [
    (a_accepted, o_create_offer), 
    (o_create_offer, o_created), 
    (o_created, o_sent_mail_and_online), 
    (o_created, notify_offer_created),  # Notify customer after offer creation
    (o_sent_mail_and_online, notify_complete)   # Notify customer after sending offer
])
subprocess_4 = gen.xor(w_call_after_offers, None)  # Adjust to optional xor to reduce repetitive loops
subprocess_5 = gen.partial_order(dependencies = [
    (a_cancelled, o_cancelled), 
    (a_cancelled, notify_cancelled)  # Notify customer of cancellation
])
subprocess_6 = gen.partial_order(dependencies = [
    (a_submitted, notify_submitted),  # Notify customer after submission
    (notify_submitted, subprocess_0)  # Handle leads after notification
])
subprocess_7 = gen.xor(None, subprocess_3)
subprocess_8 = gen.xor(a_complete, subprocess_5)
subprocess_9 = gen.xor(None, subprocess_6)
subprocess_10 = gen.partial_order(dependencies = [(subprocess_2, subprocess_7)])
subprocess_11 = gen.xor(subprocess_4, subprocess_8) # Adjust to optional xor for flexibility
subprocess_12 = gen.xor(subprocess_1, subprocess_10) # Adjust to optional xor for flexibility

final_model = gen.partial_order(dependencies = [
    (a_create_application, subprocess_9), 
    (subprocess_9, subprocess_12), 
    (subprocess_12, subprocess_11)])
