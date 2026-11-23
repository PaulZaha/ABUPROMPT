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

# Bounded rework: leads handling (1 or 2 times)
handle_leads_twice = gen.partial_order(dependencies=[(w_handle_leads.copy(), w_handle_leads.copy())])
handle_leads_bounded = gen.xor(w_handle_leads, handle_leads_twice)

# Bounded rework: application completion (1 or 2 times)
complete_app_twice = gen.partial_order(dependencies=[(w_complete_application.copy(), w_complete_application.copy())])
complete_app_bounded = gen.xor(w_complete_application, complete_app_twice)

# Optional concept
concept_opt = gen.xor(None, a_concept)

# Calls after offers: 0, 1, or 2 attempts (only if an offer was sent)
calls_twice = gen.partial_order(dependencies=[(w_call_after_offers.copy(), w_call_after_offers.copy())])
calls_bounded_opt = gen.xor(None, w_call_after_offers, calls_twice)

# Cancellation chain
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Offers branch: Accepted -> Create Offer -> Created -> Sent -> (0..2 calls)
offers_branch = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, calls_bounded_opt)
])

# Offers path optional
offers_path_optional = gen.xor(None, offers_branch)

# Finalization decision
finalization = gen.xor(a_complete, cancel_chain)

# Overall process with concurrency and simplified sequencing
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, handle_leads_bounded),
    (a_submitted, complete_app_bounded),
    (handle_leads_bounded, concept_opt),
    (complete_app_bounded, concept_opt),
    (concept_opt, offers_path_optional),
    (offers_path_optional, finalization)
])