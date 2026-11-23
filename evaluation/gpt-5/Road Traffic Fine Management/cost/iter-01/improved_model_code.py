from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Cap payment attempts to avoid unbounded internal handling cost
payment_single = payment
payment_first = payment.copy()
payment_second = payment.copy()

two_attempts = gen.xor(
    payment_single,
    gen.partial_order(dependencies=[(payment_first, payment_second)])
)

# Execute penalty/notification only if escalation is needed, then outsource
escalation_path = gen.partial_order(
    dependencies=[
        (insert_fine_notification, add_penalty),
        (add_penalty, send_for_credit_collection)
    ]
)
optional_escalation = gen.xor(None, escalation_path)

# Lean end-to-end sequence: Create -> Send -> Pay (1-2 tries) -> optionally escalate
final_model = gen.partial_order(
    dependencies=[
        (create_fine, send_fine),
        (send_fine, two_attempts),
        (two_attempts, optional_escalation)
    ]
)