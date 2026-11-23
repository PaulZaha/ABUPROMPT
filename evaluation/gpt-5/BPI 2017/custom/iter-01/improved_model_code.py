from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Original activities
na_create_application = gen.activity('A_Create Application')
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

# Customer communication activities (new)
c_ack_submission = gen.activity('C_Acknowledge Submission')
c_status_leads = gen.activity('C_Status Update: Lead Handling')
c_status_completion = gen.activity('C_Status Update: Application In Progress')
c_inform_concept = gen.activity('C_Inform: Concept Selected')
c_inform_offer_ready = gen.activity('C_Inform: Offer Ready')
c_confirm_offer_sent = gen.activity('C_Confirm: Offer Sent')
c_call_summary = gen.activity('C_Summary: Post-Offer Call')
c_confirm_completion = gen.activity('C_Confirm: Application Completed')
c_cancel_notice = gen.activity('C_Notice: Application Cancelled')

# Lead handling loop with customer status updates after each iteration
leads_iteration = gen.partial_order(dependencies=[(w_handle_leads, c_status_leads)])
subprocess_0 = gen.loop(leads_iteration, None)

# Application completion loop with customer status updates after each iteration
completion_iteration = gen.partial_order(dependencies=[(w_complete_application, c_status_completion)])
subprocess_1 = gen.loop(completion_iteration, None)

# Optional concept selection with customer information
subprocess_2 = gen.xor(None, gen.partial_order(dependencies=[(a_concept, c_inform_concept)]))

# Offer creation/sending sequence with customer notifications
subprocess_3 = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, c_inform_offer_ready),
    (c_inform_offer_ready, o_sent_mail_and_online),
    (o_sent_mail_and_online, c_confirm_offer_sent)
])
subprocess_7 = gen.xor(None, subprocess_3)  # Optional offers path

# Post-offer calls loop with customer call summaries after each iteration
call_iteration = gen.partial_order(dependencies=[(w_call_after_offers, c_call_summary)])
subprocess_4 = gen.loop(call_iteration, None)
subprocess_after_offers = gen.xor(None, subprocess_4)  # Make post-offer calls optional

# Cancellation path with customer notice
subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, c_cancel_notice)])

# Completion path with customer confirmation
complete_notify = gen.partial_order(dependencies=[(a_complete, c_confirm_completion)])
subprocess_8 = gen.xor(complete_notify, subprocess_5)  # Finalization choice

# Submission acknowledgement before lead handling
subprocess_6 = gen.partial_order(dependencies=[(a_submitted, c_ack_submission), (c_ack_submission, subprocess_0)])
subprocess_9 = gen.xor(None, subprocess_6)  # Optional submission path

# Final model: sequence preserving original intent, with customer communications integrated
final_model = gen.partial_order(dependencies=[
    (na_create_application, subprocess_9),
    (subprocess_9, subprocess_1),
    (subprocess_1, subprocess_2),
    (subprocess_2, subprocess_7),
    (subprocess_7, subprocess_after_offers),
    (subprocess_after_offers, subprocess_8)
])