
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
validate_fine = gen.activity('Validate Fine') # New validation step
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(validate_fine, send_fine), (insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, send_for_credit_collection, subprocess_1)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_0), (subprocess_0, subprocess_2)])
