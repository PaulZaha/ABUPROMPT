from generator.model_generator import ModelGenerator

gen = ModelGenerator()

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

# Cap lead handling to one rework and make it skippable (STP)
opt_second_handle = gen.xor(None, w_handle_leads.copy())
sub_leads_rework_once = gen.partial_order(dependencies=[(w_handle_leads, opt_second_handle)])
sub_leads_optional = gen.xor(None, sub_leads_rework_once)

# Cap application completion to one rework
opt_second_complete = gen.xor(None, w_complete_application.copy())
sub_complete_once = gen.partial_order(dependencies=[(w_complete_application, opt_second_complete)])

# Optional concept preparation
sub_concept_opt = gen.xor(None, a_concept)

# Acceptance and offer chain (only for completion branch)
sub_accept_offer_chain = gen.partial_order(dependencies=[(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])

# Optional follow-up call after offers
sub_call_opt = gen.xor(None, w_call_after_offers)

# Completion branch: accept/offer -> (optional) call -> complete
sub_completion_path = gen.partial_order(dependencies=[(sub_accept_offer_chain, sub_call_opt), (sub_call_opt, a_complete)])

# Cancellation branch
sub_cancellation_path = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Finalize by completing or canceling
sub_finalize = gen.xor(sub_completion_path, sub_cancellation_path)

# Streamlined end-to-end sequence
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, sub_leads_optional),
    (sub_leads_optional, sub_complete_once),
    (sub_complete_once, sub_concept_opt),
    (sub_concept_opt, sub_finalize)
])