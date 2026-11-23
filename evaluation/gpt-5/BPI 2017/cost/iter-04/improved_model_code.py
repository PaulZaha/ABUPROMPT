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

# Optional, single-pass manual lead handling instead of an unbounded loop
lead_handling_opt = gen.xor(None, w_handle_leads)
after_submission = gen.partial_order(dependencies=[(a_submitted, lead_handling_opt)])
optional_submission = gen.xor(None, after_submission)

# Optional concept step
concept_opt = gen.xor(None, a_concept)

# Optional single follow-up call after sending the offer
call_after_offer_opt = gen.xor(None, w_call_after_offers)

# Offer path with optional follow-up call; executed only if the offer branch is selected
offer_and_followup = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, call_after_offer_opt)
])
offer_opt = gen.xor(None, offer_and_followup)

# Cancellation path: make operational cancellation optional
cancel_seq = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
cancel_opt = gen.xor(None, cancel_seq)
finalization = gen.xor(a_complete, cancel_opt)

# Linearized single-pass main flow (no rework loops)
final_model = gen.partial_order(dependencies=[
    (a_create_application, optional_submission),
    (optional_submission, w_complete_application),
    (w_complete_application, concept_opt),
    (concept_opt, offer_opt),
    (offer_opt, finalization)
])