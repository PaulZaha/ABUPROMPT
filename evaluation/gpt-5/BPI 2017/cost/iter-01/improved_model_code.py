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
o_sent_online = gen.activity('O_Sent (online)')
o_sent_mail = gen.activity('O_Sent (mail)')
w_call_after_offers = gen.activity('W_Call after offers')
a_complete = gen.activity('A_Complete')
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')

# Optional and controlled rework constructs
handle_leads_opt = gen.xor(None, w_handle_leads)

# Allow at most one rework of completing the application
complete_app_rework = w_complete_application.copy()
complete_rework_opt = gen.xor(None, complete_app_rework)

# Optional concept step
concept_opt = gen.xor(None, a_concept)

# Choose a single (cheapest) sending channel
send_channel_choice = gen.xor(o_sent_online, o_sent_mail)

# Optional single follow-up call only if an offer was sent
call_after_offer_opt = gen.xor(None, w_call_after_offers)

# Offer chain gated behind acceptance; follow-up call occurs only if sending happened
offer_chain_group = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, send_channel_choice),
    (send_channel_choice, call_after_offer_opt)
])
offer_chain_opt = gen.xor(None, offer_chain_group)

# End-state choice: complete vs cancel (with cancellation handling)
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
end_choice = gen.xor(a_complete, cancel_chain)

# Final streamlined sequence to minimize rework and duplicated effort
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, handle_leads_opt),
    (handle_leads_opt, w_complete_application),
    (w_complete_application, complete_rework_opt),
    (complete_rework_opt, concept_opt),
    (concept_opt, offer_chain_opt),
    (offer_chain_opt, end_choice)
])