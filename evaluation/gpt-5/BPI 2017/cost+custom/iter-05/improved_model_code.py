from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities (existing)
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

# New automated communications (to reduce cost and keep customer informed)
o_submission_confirmation = gen.activity('O_Submission Confirmation')
o_request_missing_info = gen.activity('O_Request Missing Info')
o_offer_reminder = gen.activity('O_Offer Reminder')
o_completion_notice = gen.activity('O_Completion Notice')
o_cancellation_notice = gen.activity('O_Cancellation Notice')

# Optional single manual lead handling (replaces unlimited loop)
optional_lead_handling = gen.xor(None, w_handle_leads)

# Limit completion rework to max two attempts with automated info request in between
w_complete_application_second = w_complete_application.copy()
second_attempt_seq = gen.partial_order(dependencies=[(o_request_missing_info, w_complete_application_second)])
optional_second_attempt = gen.xor(None, second_attempt_seq)
complete_application_block = gen.partial_order(dependencies=[(w_complete_application, optional_second_attempt)])

# Optional concept phase
optional_concept = gen.xor(None, a_concept)

# Offer creation and sending sequence
offer_sequence = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online)
])

# Automated reminders, then optional single escalation call
reminder_loop = gen.loop(None, o_offer_reminder)  # 0..n automated reminders
optional_followup_call = gen.xor(None, w_call_after_offers)  # at most one manual call if needed

# Closure with customer notices
completion_with_notice = gen.partial_order(dependencies=[(a_complete, o_completion_notice)])
cancellation_with_notice = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, o_cancellation_notice)])
closure = gen.xor(completion_with_notice, cancellation_with_notice)

# Overall flow
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_submission_confirmation),
    (a_submitted, optional_lead_handling),
    (a_submitted, complete_application_block),
    (complete_application_block, optional_concept),
    (optional_concept, offer_sequence),
    (offer_sequence, reminder_loop),
    (reminder_loop, optional_followup_call),
    (optional_followup_call, closure)
])