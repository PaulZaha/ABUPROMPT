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

# 0..n lead handling after submission (skippable as a whole)
handle_leads_loop = gen.loop(None, w_handle_leads)
submission_flow = gen.partial_order(dependencies=[(a_submitted, handle_leads_loop)])
submission_opt = gen.xor(None, submission_flow)

# Concept can start early and is optional
concept_opt = gen.xor(None, a_concept)

# Offer creation and follow-up calls (0..n) only after sending the offer
calls_loop = gen.loop(None, w_call_after_offers)
offer_subprocess = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, calls_loop)
])
offer_block = gen.xor(None, offer_subprocess)

# Closing: either complete, or cancel -> cancel registered
close_subprocess = gen.xor(
    a_complete,
    gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
)

# Overall process: maximize concurrency, minimize rework, and gate closing correctly
final_model = gen.partial_order(dependencies=[
    (a_create_application, submission_opt),
    (a_create_application, w_complete_application),
    (a_create_application, concept_opt),
    (concept_opt, offer_block),
    (w_complete_application, close_subprocess),
    (offer_block, close_subprocess)
])