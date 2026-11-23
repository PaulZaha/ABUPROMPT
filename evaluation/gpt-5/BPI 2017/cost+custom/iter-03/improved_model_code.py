from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
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

# New automated/customer notification activities
o_submission_ack = gen.activity('O_Submission Acknowledgement')
o_lead_scoring = gen.activity('O_Automated Lead Scoring')
o_in_review_update = gen.activity('O_Status Update: In Review')
o_accept_update = gen.activity('O_Status Update: Accepted')
o_auto_reminder = gen.activity('O_Automated Offer Reminder')
o_final_notification = gen.activity('O_Final Decision Notification')

# Restructured/optimized control nodes
opt_handle_leads = gen.xor(None, w_handle_leads)  # optional manual lead handling after automated scoring
rework_once = gen.xor(None, w_complete_application.copy())  # allow at most one rework of completion
concept_opt = gen.xor(None, a_concept)  # concept is optional
reminder_loop = gen.loop(None, o_auto_reminder)  # 0..n automated reminders
manual_call_opt = gen.xor(None, w_call_after_offers)  # single optional manual call escalation
cancel_seq = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
final_outcome = gen.xor(a_complete, cancel_seq)  # either complete or cancel path

# Final streamlined model
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_submission_ack),
    (o_submission_ack, o_lead_scoring),
    (o_lead_scoring, opt_handle_leads),
    (opt_handle_leads, w_complete_application),
    (w_complete_application, rework_once),
    (rework_once, o_in_review_update),
    (o_in_review_update, concept_opt),
    (concept_opt, a_accepted),
    (a_accepted, o_accept_update),
    (o_accept_update, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, reminder_loop),
    (reminder_loop, manual_call_opt),
    (manual_call_opt, final_outcome),
    (final_outcome, o_final_notification)
])