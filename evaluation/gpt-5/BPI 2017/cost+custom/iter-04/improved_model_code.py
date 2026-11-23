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

# New automated customer communications to keep customers informed
o_ack_submission = gen.activity('O_Acknowledge Submission')
o_completion_confirmation = gen.activity('O_Completion Confirmation')
o_send_reminder = gen.activity('O_Send Reminder')

# Cost-reduction structures
# Optional single lead handling instead of repeated manual loop
x_handle_leads = gen.xor(None, w_handle_leads)
# Application completion can be repeated 0..n times (only as needed)
loop_complete = gen.loop(None, w_complete_application)
# Concept remains optional
x_concept = gen.xor(None, a_concept)
# Automated reminders 0..n times after offer is sent
r_auto_reminder = gen.loop(None, o_send_reminder)
# Optional single manual follow-up call
x_call_after = gen.xor(None, w_call_after_offers)

# End-of-case alternatives with customer notifications
p_complete = gen.partial_order(dependencies=[(a_complete, o_completion_confirmation)])
p_cancel = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
x_end = gen.xor(p_complete, p_cancel)

# Streamlined overall flow with concurrency where beneficial
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_ack_submission),
    (a_submitted, x_handle_leads),
    (a_submitted, loop_complete),
    (loop_complete, x_concept),
    (x_concept, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, r_auto_reminder),
    (o_sent_mail_and_online, x_call_after),
    (o_sent_mail_and_online, x_end)
])