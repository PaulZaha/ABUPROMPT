from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
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

# Improvements:
# - Skippable, repeatable (0..n) handling of leads after submission
handle_leads_loop = gen.loop(None, w_handle_leads)

# - Optional concept creation that, if used, must precede offer creation
concept_optional = gen.xor(None, a_concept)

# - Repeat follow-up calls 0..n before finalization (decoupled from completion/cancellation)
call_followups_loop = gen.loop(None, w_call_after_offers)

# - Cancellation path used in finalization
cancel_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])

# - Finalization choice: complete or cancel
finalization = gen.xor(a_complete, cancel_chain)

# Final combined partial order with lean dependencies to cut time/cost
final_model = gen.partial_order(
    dependencies=[
        (a_create_application, w_complete_application),
        (w_complete_application, a_submitted),
        (a_submitted, handle_leads_loop),
        (a_submitted, a_accepted),
        (a_submitted, concept_optional),
        (concept_optional, o_create_offer),
        (a_accepted, o_create_offer),
        (o_create_offer, o_created),
        (o_created, o_sent_mail_and_online),
        (o_sent_mail_and_online, call_followups_loop),
        (call_followups_loop, finalization)
    ]
)