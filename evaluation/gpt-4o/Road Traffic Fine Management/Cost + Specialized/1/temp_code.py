
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
validate_fine = gen.activity('Validate Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Added validation before sending a fine
subprocess_validate_and_send = gen.partial_order(dependencies=[(validate_fine, send_fine)])

subprocess_notification_penalty = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])
subprocess_payment_loop = gen.loop(payment, None)
subprocess_credit_collection = gen.xor(None, send_for_credit_collection, subprocess_payment_loop)

# Integrated simplified processes without unnecessary optional paths
final_model = gen.partial_order(dependencies=[
    (create_fine, subprocess_validate_and_send),
    (subprocess_validate_and_send, subprocess_notification_penalty),
    (subprocess_notification_penalty, subprocess_credit_collection)
])
