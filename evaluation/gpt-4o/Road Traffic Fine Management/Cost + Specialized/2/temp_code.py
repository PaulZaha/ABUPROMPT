
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

validate_fine_creation = gen.activity('Validate Fine Creation')
create_fine = gen.activity('Create Fine')
validate_send_fine = gen.activity('Validate Send Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')
send_payment_reminder = gen.activity('Send Payment Reminder')

subprocess_0 = gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, send_payment_reminder)
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(None, send_for_credit_collection, subprocess_1)
send_fine_process = gen.partial_order(dependencies = [(validate_send_fine, send_fine, subprocess_2)])
subprocess_4 = gen.xor(None, send_fine_process)

final_model = gen.partial_order(dependencies = [(validate_fine_creation, create_fine, subprocess_4), (subprocess_4, subprocess_3)])
