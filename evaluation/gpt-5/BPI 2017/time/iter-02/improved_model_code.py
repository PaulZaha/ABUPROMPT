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

# Make lead handling and call attempts skippable (0..n), to avoid forced work
handle_leads_0n = gen.loop(None, w_handle_leads)
call_after_offers_0n = gen.loop(None, w_call_after_offers)

# Application completion may require iterations (1..n)
complete_application_1n = gen.loop(w_complete_application, None)

# Optional concept before acceptance
concept_optional = gen.xor(None, a_concept)

# Closure (either complete or cancel -> order cancel chain as A_Cancelled -> O_Cancelled)
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
closure = gen.xor(a_complete, cancel_chain)

# Final model: single partial order with explicit minimal dependencies to maximize safe concurrency
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_create_application, handle_leads_0n),
    (a_create_application, complete_application_1n),
    (complete_application_1n, concept_optional),
    (a_submitted, a_accepted),
    (concept_optional, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, call_after_offers_0n),
    (o_sent_mail_and_online, closure)
])