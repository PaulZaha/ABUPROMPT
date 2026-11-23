from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Allow 1..n payment attempts without gating by other steps
payment_loop = gen.loop(payment, None)

# Escalation path: only if needed after payment attempts
pre_collection_seq = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])
post_payment_choice = gen.xor(None, pre_collection_seq)

# Optional internal notification in parallel with payment attempts
opt_notification = gen.xor(None, insert_fine_notification)

# Top-level: send fine, then run payment attempts and (optional) notification in parallel;
# after attempts, optionally escalate (add penalty then send to collections)
final_model = gen.partial_order(dependencies=[
    (create_fine, send_fine),
    (send_fine, payment_loop),
    (send_fine, opt_notification),
    (payment_loop, post_payment_choice)
])