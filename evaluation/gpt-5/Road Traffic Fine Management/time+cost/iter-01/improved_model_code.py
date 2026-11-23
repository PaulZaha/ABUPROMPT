from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Redo actions: apply penalty, then optionally send a notification/reminder
redo_actions = gen.partial_order(dependencies=[
    (add_penalty, gen.xor(None, insert_fine_notification))
])

# Payment cycle: at least one payment attempt; on non-payment, redo applies penalty and optional notification, then tries payment again
payment_cycle = gen.loop(payment, redo_actions)

# Escalation is optional after internal recovery attempts
escalation = gen.xor(None, send_for_credit_collection)

# Streamlined flow: Create -> Send -> Payment cycle -> optional escalation
final_model = gen.partial_order(dependencies=[
    (create_fine, send_fine),
    (send_fine, payment_cycle),
    (payment_cycle, escalation)
])