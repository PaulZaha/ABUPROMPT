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

# Optional and sequential submodels to reduce rework and manual iterations
s_handle_leads_opt = gen.xor(None, w_handle_leads)
s_concept_opt = gen.xor(None, a_concept)
s_offer_chain = gen.partial_order(dependencies=[(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])
s_offer_opt = gen.xor(None, s_offer_chain)
s_call_opt = gen.xor(None, w_call_after_offers)
s_cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
s_complete_or_cancel = gen.xor(a_complete, s_cancel_chain)

final_model = gen.partial_order(
    dependencies=[
        (a_create_application, a_submitted),
        (a_submitted, s_handle_leads_opt),
        (s_handle_leads_opt, w_complete_application),
        (w_complete_application, s_concept_opt),
        (s_concept_opt, s_offer_opt),
        (s_offer_opt, s_call_opt),
        (s_call_opt, s_complete_or_cancel)
    ]
)