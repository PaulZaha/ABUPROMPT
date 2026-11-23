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

# Optional submission with limited lead handling (0..1)
leads_optional = gen.xor(None, w_handle_leads)
submission_path = gen.partial_order(dependencies=[(a_submitted, leads_optional)])
submission_opt = gen.xor(None, submission_path)

# Completion rework limited to max 2 passes (1 mandatory + 1 optional)
comp_first = w_complete_application
comp_second = w_complete_application.copy()
optional_second_comp = gen.xor(None, comp_second)
comp_rework = gen.partial_order(dependencies=[(comp_first, optional_second_comp)])

# Optional concept (kept inside completion branch)
concept_opt = gen.xor(None, a_concept)

# Offers and conditional follow-ups: calls are 0..n and only after offer is sent
call_loop = gen.loop(None, w_call_after_offers)
offers_and_calls = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, call_loop)
])
optional_offers_and_calls = gen.xor(None, offers_and_calls)

# Completion branch: finish after comp_rework; offers/calls optional, concept in parallel
completion_branch = gen.partial_order(dependencies=[
    (comp_rework, a_complete),
    (comp_rework, optional_offers_and_calls),
    (concept_opt,)
])

# Cancellation branch
cancel_branch = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# Choose to either complete or cancel
end_choice = gen.xor(completion_branch, cancel_branch)

# Top-level: start, then run submission (optional) in parallel with the chosen end path
final_model = gen.partial_order(dependencies=[
    (a_create_application, submission_opt),
    (a_create_application, end_choice)
])