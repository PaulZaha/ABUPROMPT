from generator.model_generator import ModelGenerator

gen = ModelGenerator()

a_create_application = gen.activity('A_Create Application')
a_submitted = gen.activity('A_Submitted')
w_handle_leads = gen.activity('W_Handle leads')
w_complete_application = gen.activity('W_Complete application')
a_concept = gen.activity('A_Concept')
a_accepted = gen.activity('A_Accepted')
o_create_and_record_offer = gen.activity('O_Create & Record Offer')
o_sent_online = gen.activity('O_Sent online')
o_sent_mail = gen.activity('O_Sent mail')
w_call_after_offers = gen.activity('W_Call after offers')
a_complete = gen.activity('A_Complete')
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')

# Optional single handling of leads instead of repeated self-loop
subprocess_0 = gen.xor(None, w_handle_leads)

# Optional concept stage
subprocess_2 = gen.xor(None, a_concept)

# Offer creation consolidated and send via exclusive cheapest channel
send_choice = gen.xor(o_sent_online, o_sent_mail)
subprocess_3 = gen.partial_order(dependencies=[(a_accepted, o_create_and_record_offer), (o_create_and_record_offer, send_choice)])

# Optional single follow-up call after offers
subprocess_4 = gen.xor(None, w_call_after_offers)

# Cancellation path preserved
subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Submission followed by optional lead handling
subprocess_6 = gen.partial_order(dependencies=[(a_submitted, subprocess_0)])

# Optional offers process
subprocess_7 = gen.xor(None, subprocess_3)

# Finish: either complete or cancel
subprocess_8 = gen.xor(a_complete, subprocess_5)

# Optional submission path remains
subprocess_9 = gen.xor(None, subprocess_6)

# One-time completion then concept/offers (no loop)
subprocess_12 = gen.partial_order(dependencies=[(w_complete_application, subprocess_2), (subprocess_2, subprocess_7)])

# Single optional call followed by finish (no outer redo loop)
subprocess_11 = gen.partial_order(dependencies=[(subprocess_4, subprocess_8)])

final_model = gen.partial_order(dependencies=[(a_create_application, subprocess_9), (subprocess_9, subprocess_12), (subprocess_12, subprocess_11)])