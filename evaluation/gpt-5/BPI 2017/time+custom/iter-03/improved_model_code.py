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

# New customer communication activities
o_submission_confirmation = gen.activity('O_Submission Confirmation')
o_progress_update = gen.activity('O_Progress Update')
o_final_decision_notification = gen.activity('O_Final Decision Notification')

# Skippable/optimized loops and optional stages to reduce waiting
handle_leads_loop = gen.loop(None, w_handle_leads)  # 0..n lead-handling iterations
complete_application_loop = gen.loop(w_complete_application, None)  # 1..n application completion iterations
progress_updates_loop = gen.loop(None, o_progress_update)  # 0..n proactive status updates
concept_optional = gen.xor(None, a_concept)  # optional concept stage

# Offer decision and post-offer follow-up
calls_loop = gen.loop(None, w_call_after_offers)  # 0..n follow-up calls
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
decision_xor = gen.xor(a_complete, cancel_chain)  # either complete or cancel

# Final optimized process with parallelization and explicit customer notifications
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_submission_confirmation),
    (a_submitted, handle_leads_loop),
    (a_submitted, complete_application_loop),
    (a_submitted, progress_updates_loop),
    (complete_application_loop, concept_optional),
    (concept_optional, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, calls_loop),
    (calls_loop, decision_xor),
    (decision_xor, o_final_decision_notification)
])