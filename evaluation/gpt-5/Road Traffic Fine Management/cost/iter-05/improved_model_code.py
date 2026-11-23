from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Cap payment handling to 0, 1, or 2 attempts to limit admin/transaction cost
payment_once = payment
payment_twice_first = payment.copy()
payment_twice_second = payment.copy()
payment_twice = gen.partial_order(dependencies=[(payment_twice_first, payment_twice_second)])
payment_attempts = gen.xor(None, payment_once, payment_twice)

# Penalty workflow only if unpaid after attempts
penalty_sequence = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])
penalty_optional = gen.xor(None, penalty_sequence)

# Escalate to collections only after internal attempts (and optional penalty)
collection_optional = gen.xor(None, send_for_credit_collection)

final_model = gen.partial_order(dependencies=[
    (create_fine, send_fine),
    (send_fine, payment_attempts),
    (payment_attempts, penalty_optional),
    (penalty_optional, collection_optional)
])