from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Base activities
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

# Customer communication (automated)
n_submission = gen.activity('N_Submission Confirmation')
n_offer_sent = gen.activity('N_Offer Sent')
n_reminder = gen.activity('N_Reminder')
n_outcome_complete = gen.activity('N_Outcome - Completed')
n_outcome_cancelled = gen.activity('N_Outcome - Cancelled')

# Submodels
loop_handle = gen.loop(w_handle_leads, None)                 # 1..n times
loop_complete = gen.loop(w_complete_application, None)       # 1..n times
concept_opt = gen.xor(None, a_concept)                       # optional concept check

# Decision outcomes integrated with notifications
seq_complete = gen.partial_order(dependencies=[(a_complete, n_outcome_complete)])
seq_cancel = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, n_outcome_cancelled)])
decision_xor = gen.xor(seq_complete, seq_cancel)

# Post-offer engagement: optional manual call + 0..n automated reminders
call_opt = gen.xor(None, w_call_after_offers)
rem_loop = gen.loop(None, n_reminder)                        # 0..n reminders

# Top-level flow with explicit concurrency and sequencing
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, n_submission),
    (a_submitted, loop_handle),
    (a_submitted, loop_complete),
    (a_submitted, concept_opt),
    (loop_handle, a_accepted),
    (loop_complete, a_accepted),
    (concept_opt, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, n_offer_sent),
    (o_sent_mail_and_online, call_opt),
    (o_sent_mail_and_online, rem_loop),
    (o_sent_mail_and_online, decision_xor)
] )