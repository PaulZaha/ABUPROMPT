from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Optional admin stream after sending the fine (kept optional but decoupled from resolution)
notif_penalty = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])
notif_penalty_optional = gen.xor(None, notif_penalty)

# Payment attempts limited to two, then escalate
second_payment_optional = gen.xor(None, payment.copy())
escalate_after_attempts = send_for_credit_collection.copy()
payments_then_escalate = gen.partial_order(dependencies=[(payment, second_payment_optional), (second_payment_optional, escalate_after_attempts)])

# Resolution: either immediate collection or payment attempts then escalation
resolution = gen.xor(payments_then_escalate, send_for_credit_collection)

# Final model: send fine first; then in parallel start admin tasks and resolution
final_model = gen.partial_order(dependencies=[(create_fine, send_fine), (send_fine, notif_penalty_optional), (send_fine, resolution)])