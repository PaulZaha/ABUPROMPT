from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Automated reminder followed by penalty before another payment attempt
reminder_and_penalty = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])

# Payment loop: try payment; if unpaid, send reminder and add penalty, then try payment again
payment_cycle = gen.loop(payment, reminder_and_penalty)

# Escalate to credit collection only if still unpaid after the payment cycle
escalation_optional = gen.xor(None, send_for_credit_collection)

# Streamlined backbone: Create -> Send -> Payment/Reminder/Penalty loop -> Optional escalation
final_model = gen.partial_order(dependencies=[
    (create_fine, send_fine),
    (send_fine, payment_cycle),
    (payment_cycle, escalation_optional)
])