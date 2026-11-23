from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
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

# Customer notifications (non-blocking, run in parallel)
n_submission_confirmation = gen.activity('N_Submission Confirmation')
n_acceptance_notification = gen.activity('N_Acceptance Notification')
n_offer_sent_notification = gen.activity('N_Offer Sent Notification')
n_auto_reminder = gen.activity('N_Automated Reminder')
n_completion_confirmation = gen.activity('N_Completion Confirmation')
n_cancellation_notification = gen.activity('N_Cancellation Notification')

# Early parallel work (loops remain but run concurrently to reduce elapsed time)
handle_leads_loop = gen.loop(w_handle_leads, None)
complete_application_loop = gen.loop(w_complete_application, None)

# Optional concept before acceptance
concept_opt = gen.xor(None, a_concept)

# Post-offer follow-up: lightweight manual call (optional) + automated reminders (0..n)
call_optional = gen.xor(None, w_call_after_offers)
reminders_loop = gen.loop(None, n_auto_reminder)

# Decision branches with embedded notifications
complete_branch = gen.partial_order(dependencies=[(a_complete, n_completion_confirmation)])
cancel_branch = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, n_cancellation_notification)])
decision_xor = gen.xor(complete_branch, cancel_branch)

# One clear top-level partial order capturing sequencing and concurrency
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, n_submission_confirmation),
    (a_submitted, handle_leads_loop),
    (a_submitted, complete_application_loop),

    # If concept is executed, it must precede acceptance
    (concept_opt, a_accepted),

    # Acceptance occurs after early work streams finish
    (handle_leads_loop, a_accepted),
    (complete_application_loop, a_accepted),

    # Notify acceptance and proceed to offer chain
    (a_accepted, n_acceptance_notification),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),

    # Post-offer communications and decision
    (o_sent_mail_and_online, n_offer_sent_notification),
    (o_sent_mail_and_online, call_optional),
    (o_sent_mail_and_online, reminders_loop),
    (o_sent_mail_and_online, decision_xor)
])