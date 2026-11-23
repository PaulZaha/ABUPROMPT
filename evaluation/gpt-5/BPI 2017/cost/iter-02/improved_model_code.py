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

# Cap W_Handle leads to at most one rework (1x or 2x)
handle_twice_seq = gen.partial_order(dependencies=[(w_handle_leads.copy(), w_handle_leads.copy())])
handle_bounded = gen.xor(w_handle_leads, handle_twice_seq)

# Cap W_Complete application to at most one rework (1x or 2x)
complete_twice_seq = gen.partial_order(dependencies=[(w_complete_application.copy(), w_complete_application.copy())])
complete_bounded = gen.xor(w_complete_application, complete_twice_seq)

# Optional concept stage
concept_optional = gen.xor(None, a_concept)

# After sending offer: either complete directly or do one (optional) follow-up call before completing
call_then_complete_seq = gen.partial_order(dependencies=[(w_call_after_offers, a_complete.copy())])
post_offer_xor = gen.xor(a_complete, call_then_complete_seq)

# Approval path: accepted -> create offer -> created -> sent -> (complete or call+complete)
approval_seq = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, post_offer_xor)
])

# Cancellation path: cancel -> cancellation output
cancellation_seq = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Decide between proceeding to offer/complete or cancelling
decision_xor = gen.xor(approval_seq, cancellation_seq)

# Overall streamlined, cost-efficient flow
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, handle_bounded),
    (handle_bounded, complete_bounded),
    (complete_bounded, concept_optional),
    (concept_optional, decision_xor)
])