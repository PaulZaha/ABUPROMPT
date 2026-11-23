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

# Bounded handling of leads: 0, 1, or 2 attempts (optional overall)
handle_single = w_handle_leads.copy()
handle_first = w_handle_leads.copy()
handle_second = w_handle_leads.copy()
handle_two = gen.partial_order(dependencies=[(handle_first, handle_second)])
handle_seq = gen.xor(handle_single, handle_two)
handle_seq_opt = gen.xor(None, handle_seq)

# Bounded completion rework: 1 or 2 passes (mandatory at least once)
complete_single = w_complete_application.copy()
complete_first = w_complete_application.copy()
complete_second = w_complete_application.copy()
complete_two = gen.partial_order(dependencies=[(complete_first, complete_second)])
complete_seq = gen.xor(complete_single, complete_two)

# Bounded follow-ups after offer sent: 0, 1, or 2 calls
call_single = w_call_after_offers.copy()
call_first = w_call_after_offers.copy()
call_second = w_call_after_offers.copy()
call_two = gen.partial_order(dependencies=[(call_first, call_second)])
call_zero_or_one = gen.xor(None, call_single)
call_bounded = gen.xor(call_zero_or_one, call_two)

# End outcomes: complete vs cancelled (with obligatory order for cancellation)
cancellation_chain = gen.partial_order(dependencies=[(a_cancelled, o_cancelled)])
end_outcome = gen.xor(a_complete, cancellation_chain)

# Offer path (optional) with calls gated after sending the offer
offer_submodel = gen.partial_order(dependencies=[
    (a_accepted, o_create_offer),
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),
    (o_sent_mail_and_online, call_bounded)
])
offer_opt = gen.xor(None, offer_submodel)

# Concept optional
a_concept_opt = gen.xor(None, a_concept)

# Top-level: submission mandatory; early parallelism; bounded rework; clean terminalization
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, handle_seq_opt),
    (a_submitted, complete_seq),
    (complete_seq, a_concept_opt),
    (a_concept_opt, offer_opt),
    (handle_seq_opt, end_outcome),
    (complete_seq, end_outcome),
    (offer_opt, end_outcome)
])