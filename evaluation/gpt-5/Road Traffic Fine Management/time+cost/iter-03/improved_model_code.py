from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Optional notification in parallel (non-blocking)
notif_optional = gen.xor(None, insert_fine_notification)

# Limit payment to at most two attempts
payment_second = payment.copy()
second_attempt_optional = gen.xor(None, payment_second)
payment_attempts = gen.partial_order(dependencies=[(payment, second_attempt_optional)])

# Escalation path only if not paid
escalate = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])

# Decide between payment attempts or escalation (no dangling skip)
decision = gen.xor(payment_attempts, escalate)

# Main orchestration: create -> send fine; notification runs in parallel; then decide
final_model = gen.partial_order(dependencies=[(create_fine, send_fine), (send_fine, decision), (notif_optional,)])