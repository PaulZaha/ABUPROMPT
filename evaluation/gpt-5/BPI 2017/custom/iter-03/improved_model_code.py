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

# New customer communication and portal update activities
c_ack_create = gen.activity('C_Acknowledge Application Creation')
c_portal_created = gen.activity('C_Update Portal - Created')

c_subm_confirm = gen.activity('C_Submission Confirmation')
c_portal_submitted = gen.activity('C_Update Portal - Submitted')

c_status_leads = gen.activity('C_Status Update (Leads)')

c_status_completion = gen.activity('C_Status Update (Completion)')
c_reminder_docs = gen.activity('C_Reminder: Provide Missing Info')

c_concept_shared = gen.activity('C_Concept Shared with Customer')
c_portal_concept = gen.activity('C_Update Portal - Concept')

c_inform_accepted = gen.activity('C_Inform Customer of Acceptance')
c_notify_offer_ready = gen.activity('C_Notify Offer Ready')
c_confirm_offer_sent = gen.activity('C_Confirm Offer Sent')
c_portal_offer = gen.activity('C_Update Portal - Offer')

c_followup_email = gen.activity('C_Follow-up Email After Call')

c_final_confirmation = gen.activity('C_Final Confirmation')
c_portal_final = gen.activity('C_Update Portal - Completed')

c_cancellation_notice = gen.activity('C_Cancellation Notice')
c_portal_cancelled = gen.activity('C_Update Portal - Cancelled')

# Subprocesses with improved customer communication
# Leads handling with periodic status updates
subprocess_0 = gen.loop(w_handle_leads, c_status_leads)

# Application completion with periodic status updates and reminders
subprocess_1 = gen.loop(w_complete_application, gen.partial_order(dependencies=[(c_status_completion, c_reminder_docs)]))

# Optional concept with customer communication and portal update
subprocess_concept = gen.partial_order(dependencies=[(a_concept, c_concept_shared), (c_concept_shared, c_portal_concept)])
subprocess_2 = gen.xor(None, subprocess_concept)

# Acceptance to offer creation with customer notifications and portal updates
subprocess_3 = gen.partial_order(dependencies=[
    (a_accepted, c_inform_accepted),
    (c_inform_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, c_notify_offer_ready),
    (c_notify_offer_ready, o_sent_mail_and_online),
    (o_sent_mail_and_online, c_confirm_offer_sent),
    (c_confirm_offer_sent, c_portal_offer)
])

# Calls after offers with follow-up emails
subprocess_4 = gen.loop(w_call_after_offers, c_followup_email)

# Cancellation path with customer notification and portal update
subprocess_5 = gen.partial_order(dependencies=[
    (a_cancelled, c_cancellation_notice),
    (c_cancellation_notice, o_cancelled),
    (o_cancelled, c_portal_cancelled)
])

# Submission path with confirmation, portal update, and leads handling
subprocess_6 = gen.partial_order(dependencies=[
    (a_submitted, c_subm_confirm),
    (c_subm_confirm, c_portal_submitted),
    (c_portal_submitted, subprocess_0)
])

# Optional offer flow
subprocess_7 = gen.xor(None, subprocess_3)

# Completion path with final confirmation and portal update vs. cancellation path
subprocess_complete_comm = gen.partial_order(dependencies=[(a_complete, c_final_confirmation), (c_final_confirmation, c_portal_final)])
subprocess_8 = gen.xor(subprocess_complete_comm, subprocess_5)

# Optional submission & leads path
subprocess_9 = gen.xor(None, subprocess_6)

# Concept then optional offer flow
subprocess_10 = gen.partial_order(dependencies=[(subprocess_2, subprocess_7)])

# Optional call loop before finalization (complete or cancel)
subprocess_11 = gen.partial_order(dependencies=[(gen.xor(None, subprocess_4), subprocess_8)])

# Main loop: complete application, then concept/offer progression
subprocess_12 = gen.loop(subprocess_1, subprocess_10)

# Final model with early acknowledgments and ordered progression
final_model = gen.partial_order(dependencies=[
    (a_create_application, c_ack_create),
    (c_ack_create, c_portal_created),
    (c_portal_created, subprocess_9),
    (subprocess_9, subprocess_12),
    (subprocess_12, subprocess_11)
])