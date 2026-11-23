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

# New/automated customer communication activities
o_submission_confirmation = gen.activity('O_Submission Confirmation Sent')
o_request_info = gen.activity('O_Request Missing Info')
o_reminder_sent = gen.activity('O_Reminder Sent')
o_status_update = gen.activity('O_Status Update Sent')
o_cancellation_notice = gen.activity('O_Cancellation Notice Sent')

# Handle leads: allow at most one rework (cost cap)
w_handle_leads_second = w_handle_leads.copy()
handle_leads_second_opt = gen.xor(None, w_handle_leads_second)
handle_leads_block = gen.partial_order(dependencies=[(w_handle_leads, handle_leads_second_opt)])

# Complete application: one controlled rework preceded by automated info request
w_complete_application_second = w_complete_application.copy()
rework_pack = gen.partial_order(dependencies=[(o_request_info, w_complete_application_second)])
rework_pack_opt = gen.xor(None, rework_pack)
complete_block = gen.partial_order(dependencies=[(w_complete_application, rework_pack_opt)])

# Offer creation/sending with automated follow-ups and capped manual call
reminder_second_opt = gen.xor(None, o_reminder_sent.copy())
optional_manual_call = gen.xor(None, w_call_after_offers)
post_offer_followup = gen.partial_order(dependencies=[(o_reminder_sent, reminder_second_opt), (reminder_second_opt, optional_manual_call)])

offer_core = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, post_offer_followup)
])

offer_opt = gen.xor(None, offer_core)
concept_opt = gen.xor(None, a_concept)
concept_then_offer = gen.partial_order(dependencies=[(concept_opt, offer_opt)])

# Finalization paths with customer notifications
completion_chain = gen.partial_order(dependencies=[(a_complete, o_status_update)])
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, o_cancellation_notice)])
final_decision = gen.xor(completion_chain, cancel_chain)

# Overall flow: confirmation runs in parallel with lead handling after submission
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_submission_confirmation),
    (a_submitted, handle_leads_block),
    (handle_leads_block, complete_block),
    (complete_block, concept_then_offer),
    (concept_then_offer, final_decision)
])