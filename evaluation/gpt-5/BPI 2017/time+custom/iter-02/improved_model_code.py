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

# Customer communication activities (to keep customer informed)
c_submission_confirmation = gen.activity('C_Submission Confirmation')
c_acceptance_notification = gen.activity('C_Acceptance Notification')
c_offer_sent_notification = gen.activity('C_Offer Sent Notification')
c_completion_notification = gen.activity('C_Completion Notification')
c_cancellation_notification = gen.activity('C_Cancellation Notification')

# Cap rework to one optional retry for leads handling and application completion
leads_rework = gen.xor(None, w_handle_leads.copy())
complete_rework = gen.xor(None, w_complete_application.copy())

# Optional follow-up call after offers (single optional call)
call_optional = gen.xor(None, w_call_after_offers)

# Optional concept prior to acceptance
concept_optional = gen.xor(None, a_concept)

# Early cancellation branch (with customer notification)
early_cancel_branch = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, c_cancellation_notification)])

# Final outcome branches (with customer notification)
branch_complete = gen.partial_order(dependencies=[(a_complete, c_completion_notification)])
late_cancel_branch = early_cancel_branch.copy()
post_outcome_choice = gen.xor(branch_complete, late_cancel_branch)

# Continue path: concept (optional) -> acceptance -> offer creation -> sent, with notifications and optional call
continue_path = gen.partial_order(dependencies=[
    (concept_optional, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (a_accepted, c_acceptance_notification),
    (o_sent_mail_and_online, c_offer_sent_notification),
    (o_sent_mail_and_online, call_optional),
    (o_sent_mail_and_online, post_outcome_choice)
])

# Decision after submission work: proceed or cancel early
decision_stage = gen.xor(continue_path, early_cancel_branch)

# Final model: enforce submission, parallelize post-submission work, then decision
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, w_handle_leads),
    (w_handle_leads, leads_rework),
    (a_submitted, w_complete_application),
    (w_complete_application, complete_rework),
    (a_submitted, c_submission_confirmation),
    (w_handle_leads, decision_stage),
    (leads_rework, decision_stage),
    (w_complete_application, decision_stage),
    (complete_rework, decision_stage),
    (c_submission_confirmation, decision_stage)
])