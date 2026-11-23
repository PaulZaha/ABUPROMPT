from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Consolidated front-end step to avoid creating fines that are not sent and to automate notification
issue_fine = gen.activity('Issue Fine')

# Bounded payment attempts: either one attempt or two attempts in sequence
payment = gen.activity('Payment')
payment_second = payment.copy()
payment_once = payment.copy()

payment_two_attempts = gen.partial_order(dependencies=[(payment, payment_second)])
payment_attempts = gen.xor(payment_once, payment_two_attempts)

# Costly escalation only if needed after attempts
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')

escalate_path = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])
post_payment = gen.xor(None, escalate_path)

# Overall sequence: Issue -> Attempts -> (Optionally) Escalate
final_model = gen.partial_order(dependencies=[(issue_fine, payment_attempts), (payment_attempts, post_payment)])