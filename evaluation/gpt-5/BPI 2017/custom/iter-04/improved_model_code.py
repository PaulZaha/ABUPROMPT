from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
A_Create_Application = gen.activity('A_Create Application')
A_Submitted = gen.activity('A_Submitted')
W_Handle_leads = gen.activity('W_Handle leads')
W_Complete_application = gen.activity('W_Complete application')
A_Concept = gen.activity('A_Concept')
A_Accepted = gen.activity('A_Accepted')
O_Create_Offer = gen.activity('O_Create Offer')
O_Created = gen.activity('O_Created')
O_Sent_mail_and_online = gen.activity('O_Sent (mail and online)')
W_Call_after_offers = gen.activity('W_Call after offers')
A_Complete = gen.activity('A_Complete')
A_Cancelled = gen.activity('A_Cancelled')
O_Cancelled = gen.activity('O_Cancelled')

# New customer communication activities
C_Confirm_Submission = gen.activity('C_Confirm Submission')
C_Status_Update_Leads = gen.activity('C_Status Update (Leads)')
C_Status_Update_Processing = gen.activity('C_Status Update (Processing)')
C_Post_Offer_Update = gen.activity('C_Post-Offer Update')
C_Notify_Outcome = gen.activity('C_Notify Outcome')

# Lead handling loop with customer updates after each iteration
leads_iteration = gen.partial_order(dependencies=[(W_Handle_leads, C_Status_Update_Leads)])
leads_loop = gen.loop(leads_iteration, None)

# Submission confirmation prior to lead handling
submitted_with_ack_and_leads = gen.partial_order(
    dependencies=[(A_Submitted, C_Confirm_Submission), (C_Confirm_Submission, leads_loop)]
)
submitted_opt = gen.xor(None, submitted_with_ack_and_leads)

# Application processing loop with customer updates
processing_iteration = gen.partial_order(dependencies=[(W_Complete_application, C_Status_Update_Processing)])
processing_loop = gen.loop(processing_iteration, None)

# Optional concept step
concept_opt = gen.xor(None, A_Concept)

# Offer chain (optional)
offer_chain = gen.partial_order(
    dependencies=[(A_Accepted, O_Create_Offer), (O_Create_Offer, O_Created), (O_Created, O_Sent_mail_and_online)]
)
offer_opt = gen.xor(None, offer_chain)

# Concept must precede offers if chosen
concept_then_offer = gen.partial_order(dependencies=[(concept_opt, offer_opt)])

# Post-offer follow-up calls with updates after each call
post_offer_iteration = gen.partial_order(dependencies=[(W_Call_after_offers, C_Post_Offer_Update)])
post_offer_loop = gen.loop(post_offer_iteration, None)

# Final decision (complete or cancel) and outcome notification
cancel_flow = gen.partial_order(dependencies=[(A_Cancelled, O_Cancelled)])
end_choice = gen.xor(A_Complete, cancel_flow)
notify_outcome = gen.partial_order(dependencies=[(end_choice, C_Notify_Outcome)])

# Final model: sequence ensures communications at each stage
final_model = gen.partial_order(
    dependencies=[
        (A_Create_Application, submitted_opt),
        (submitted_opt, processing_loop),
        (processing_loop, concept_then_offer),
        (concept_then_offer, post_offer_loop),
        (post_offer_loop, notify_outcome),
    ]
)