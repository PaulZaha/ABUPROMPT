from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Original activities
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

# New customer communication activities to keep the customer informed
c_notify_submission_received = gen.activity('C_Notify Submission Received')
c_update_lead_handling = gen.activity('C_Update Lead Handling Status')
c_update_application_progress = gen.activity('C_Update Application Progress')
c_notify_concept_shared = gen.activity('C_Notify Concept Shared')
c_notify_accepted = gen.activity('C_Notify Acceptance')
c_send_call_summary = gen.activity('C_Send Call Summary')
c_notify_completed = gen.activity('C_Notify Completion')
c_notify_cancellation = gen.activity('C_Notify Cancellation')

# Lead handling loop with customer update each iteration
po_handle_leads_notify = gen.partial_order(dependencies=[(w_handle_leads, c_update_lead_handling)])
subprocess_0 = gen.loop(po_handle_leads_notify, None)

# Application completion loop with customer update each iteration
po_complete_and_update = gen.partial_order(dependencies=[(w_complete_application, c_update_application_progress)])
subprocess_1 = gen.loop(po_complete_and_update, None)

# Optional concept with customer notification when produced
po_concept_and_notify = gen.partial_order(dependencies=[(a_concept, c_notify_concept_shared)])
subprocess_2 = gen.xor(None, po_concept_and_notify)

# Accepted -> notify customer -> create offer -> created -> sent
subprocess_3 = gen.partial_order(dependencies=[(a_accepted, c_notify_accepted), (c_notify_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])

# Call after offers loop with post-call summary to customer
po_call_and_summary = gen.partial_order(dependencies=[(w_call_after_offers, c_send_call_summary)])
subprocess_4 = gen.loop(po_call_and_summary, None)

# Cancellation path with customer notification
subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, c_notify_cancellation)])

# After submission, notify customer then proceed to lead handling loop
subprocess_6 = gen.partial_order(dependencies=[(a_submitted, c_notify_submission_received), (c_notify_submission_received, subprocess_0)])

# Optional offer creation sequence
subprocess_7 = gen.xor(None, subprocess_3)

# Completion path notifies customer; xor with cancellation path
po_complete_notify = gen.partial_order(dependencies=[(a_complete, c_notify_completed)])
subprocess_8 = gen.xor(po_complete_notify, subprocess_5)

# Optional submission/lead-handling branch
subprocess_9 = gen.xor(None, subprocess_6)

# Concept (optional) precedes optional offer creation
subprocess_10 = gen.partial_order(dependencies=[(subprocess_2, subprocess_7)])

# Post-offer interaction loop; each completion/cancellation triggers another interaction cycle
subprocess_11 = gen.loop(subprocess_4, subprocess_8)

# Application completion loop interleaved with concept/offer path
subprocess_12 = gen.loop(subprocess_1, subprocess_10)

# Overall process order preserved
final_model = gen.partial_order(dependencies=[(a_create_application, subprocess_9), (subprocess_9, subprocess_12), (subprocess_12, subprocess_11)])