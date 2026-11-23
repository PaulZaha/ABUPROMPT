from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Couple payment attempts with automated penalty between attempts to avoid manual delays
payment_cycle = gen.loop(payment, add_penalty)

# Escalation is optional and follows the payment cycle, enabling immediate escalation when needed
escalate_optional = gen.xor(None, send_for_credit_collection)

# Parallelize Send Fine with system publication (Insert Fine Notification),
# start payment as soon as the fine is published, then optionally escalate
final_model = gen.partial_order(dependencies=[
    (create_fine, insert_fine_notification),
    (create_fine, send_fine),
    (insert_fine_notification, payment_cycle),
    (payment_cycle, escalate_optional)
])