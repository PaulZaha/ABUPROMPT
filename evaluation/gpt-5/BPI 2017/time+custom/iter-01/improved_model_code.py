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

# New customer communication steps for transparency
o_confirm_submission = gen.activity('O_Confirm Submission')
o_status_update = gen.activity('O_Status Update')
o_notify_acceptance = gen.activity('O_Notify Acceptance')
o_inform_cancellation = gen.activity('O_Inform Cancellation')

# Reworked loops to avoid unnecessary rework and enable optional repetitions
lead_loop = gen.loop(w_handle_leads, None)              # 1..n (maintain at least one pass, allow rework only if needed)
complete_loop = gen.loop(w_complete_application, None)  # 1..n
status_loop = gen.loop(None, o_status_update)           # 0..n optional status updates
calls_loop = gen.loop(None, w_call_after_offers)        # 0..n optional follow-up calls after offer

# Optional concept before acceptance
opt_concept = gen.xor(None, a_concept)

# Cancellation branch with customer communication
cancel_seq = gen.partial_order(dependencies=[(a_cancelled, o_cancelled), (o_cancelled, o_inform_cancellation)])
outcome_xor = gen.xor(a_complete, cancel_seq)

# Final model: a single partial order encoding the full flow with concurrency where possible
final_model = gen.partial_order(dependencies=[
    (a_create_application, a_submitted),
    (a_submitted, o_confirm_submission),

    # After confirmation, run early work in parallel and allow optional status updates and concept
    (o_confirm_submission, lead_loop),
    (o_confirm_submission, complete_loop),
    (o_confirm_submission, status_loop),
    (o_confirm_submission, opt_concept),

    # Acceptance requires lead handling, application completion, and the (optional) concept decision
    (lead_loop, a_accepted),
    (complete_loop, a_accepted),
    (opt_concept, a_accepted),

    # Notify acceptance immediately and start offer production without delay
    (a_accepted, o_notify_acceptance),
    (a_accepted, o_create_offer),

    # Offer creation and sending
    (o_create_offer, o_created),
    (o_created, o_sent_mail_and_online),

    # After sending the offer, optional follow-up calls and the final outcome decision
    (o_sent_mail_and_online, calls_loop),
    (o_sent_mail_and_online, outcome_xor),
])