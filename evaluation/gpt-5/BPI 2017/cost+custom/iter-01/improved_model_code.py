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

# New, low-cost customer communications
o_notify_received = gen.activity('O_Notify Application Received')
o_send_reminder = gen.activity('O_Send Reminder')
o_notify_completed = gen.activity('O_Notify Application Completed')
o_notify_cancelled = gen.activity('O_Notify Application Cancelled')

# Optional and iterative submodels
leads_opt = gen.xor(None, w_handle_leads)            # optional lead handling (no more unbounded loop)
concept_opt = gen.xor(None, a_concept)               # optional concept before acceptance
reminder_loop = gen.loop(None, o_send_reminder)      # 0..n automated reminders (cheap)
call_opt = gen.xor(None, w_call_after_offers)        # escalate to a single manual call only if needed

# Outcome branches with customer notifications
complete_seq = gen.partial_order(dependencies=[(a_complete, o_notify_completed)])
cancel_seq = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, o_notify_cancelled)])
decision_xor = gen.xor(complete_seq, cancel_seq)

# Final model: streamlined flow with proactive comms and minimized manual rework
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_notify_received),
    (a_submitted, leads_opt),
    (leads_opt, w_complete_application),
    (w_complete_application, concept_opt),
    (w_complete_application, a_accepted),
    (concept_opt, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, reminder_loop),
    (o_sent_mail_and_online, decision_xor),
    (reminder_loop, call_opt)
])