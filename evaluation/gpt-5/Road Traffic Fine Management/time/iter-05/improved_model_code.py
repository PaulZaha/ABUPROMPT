from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Optional communications that can run without blocking payment
optional_send_fine = gen.xor(None, send_fine)
optional_insert_notification = gen.xor(None, insert_fine_notification)

# Escalation path if not paid: add penalty then send to credit collection
escalate = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])

# Decision after a single payment attempt: either skip (paid) or escalate
after_payment_decision = gen.xor(None, escalate)

# Concurrency after creating the fine: start payment immediately, while comms proceed in parallel
final_model = gen.partial_order(dependencies=[
    (create_fine, optional_send_fine),
    (create_fine, optional_insert_notification),
    (create_fine, payment),
    (payment, after_payment_decision)
])