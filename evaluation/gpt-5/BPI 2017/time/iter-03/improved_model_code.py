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

leads_loop_opt = gen.loop(None, w_handle_leads)
comp_loop = gen.loop(w_complete_application, None)
concept_opt = gen.xor(None, a_concept)
calls_loop_opt = gen.loop(None, w_call_after_offers)
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
termination = gen.xor(a_complete, cancel_chain)

final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_create_application, comp_loop),
    (a_submitted, leads_loop_opt),
    (a_submitted, concept_opt),
    (concept_opt, a_accepted),
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, calls_loop_opt),
    (comp_loop, termination)
])