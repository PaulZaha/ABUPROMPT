from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
a_create_application = gen.activity('A_Create Application')
a_submitted = gen.activity('A_Submitted')
w_handle_leads = gen.activity('W_Handle leads')
w_complete_application = gen.activity('W_Complete application')
a_concept = gen.activity('A_Concept')
a_accepted = gen.activity('A_Accepted')
o_generate_and_send_offer = gen.activity('O_Generate and Send Offer')
w_call_after_offers = gen.activity('W_Call after offers')
a_complete = gen.activity('A_Complete')
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')

# Improvements: bound/optional rework and follow-ups
optional_lead_handling = gen.xor(None, w_handle_leads)  # at most one follow-up on leads
second_completion = w_complete_application.copy()       # allow at most one rework
optional_second_completion = gen.xor(None, second_completion)
concept_optional = gen.xor(None, a_concept)             # concept is optional
optional_call = gen.xor(None, w_call_after_offers)      # at most one post-offer call

# Finalization: either complete or cancel (cancel -> offer cancellation)
final_outcome = gen.xor(
    a_complete,
    gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
)

# End-to-end chain executed only if the application is submitted
process_chain = gen.partial_order(dependencies=[
    (a_submitted, optional_lead_handling),
    (optional_lead_handling, w_complete_application),
    (w_complete_application, optional_second_completion),
    (optional_second_completion, concept_optional),
    (concept_optional, a_accepted),
    (a_accepted, o_generate_and_send_offer),
    (o_generate_and_send_offer, optional_call),
    (optional_call, final_outcome)
])

# Gate the whole chain behind submission to avoid work on non-submitted applications
full_process_xor = gen.xor(None, process_chain)

final_model = gen.partial_order(dependencies=[(a_create_application, full_process_xor)])