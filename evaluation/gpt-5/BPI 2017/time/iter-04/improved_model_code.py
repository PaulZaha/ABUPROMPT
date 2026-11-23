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

# Optional/one-pass variants replacing previous loops
lead_opt = gen.xor(None, w_handle_leads)           # optional lead handling to avoid rework cycles
concept_opt = gen.xor(None, a_concept)             # optional concept, started early in parallel
call_opt = gen.xor(None, w_call_after_offers)      # single optional follow-up call after sending

# Cancellation chain kept but only taken in the end decision
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
end_choice = gen.xor(a_complete, cancel_chain)

# Final partial order accelerates the critical path and leverages concurrency
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),                # auto submission
    (a_submitted, w_complete_application),              # start completion immediately
    (a_submitted, lead_opt),                            # optional lead handling in parallel
    (a_submitted, concept_opt),                         # optional concept in parallel

    (w_complete_application, o_create_offer),           # draft offer after completion
    (o_create_offer, o_created),                        # create -> created

    (w_complete_application, a_accepted),               # acceptance processed in parallel with offer drafting
    (o_created, o_sent_mail_and_online),                # send only after offer is created
    (a_accepted, o_sent_mail_and_online),               # and after acceptance (safety control)

    (o_sent_mail_and_online, call_opt),                 # optional follow-up call, no longer gating
    (o_sent_mail_and_online, end_choice)                # complete or cancel can proceed right after sending
])