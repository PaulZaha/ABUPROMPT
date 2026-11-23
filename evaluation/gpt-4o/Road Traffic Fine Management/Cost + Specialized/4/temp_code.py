
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

validate_fine_conditions = gen.activity('Validate Fine Conditions')
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add Penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_validation = gen.xor(None, validate_fine_conditions)
subprocess_penalty = gen.xor(None, add_penalty)
subprocess_notification = gen.partial_order(dependencies=[(insert_fine_notification, subprocess_penalty)])
subprocess_credit_collection = gen.xor(None, send_for_credit_collection)
subprocess_payment = gen.loop(payment, None)

subprocess_0 = gen.partial_order(dependencies=[(send_fine, subprocess_notification)])
subprocess_1 = gen.xor(None, subprocess_0, subprocess_credit_collection)
subprocess_2 = gen.xor(None, subprocess_1)

final_model = gen.partial_order(dependencies=[(subprocess_validation, create_fine), (create_fine, subprocess_2), (subprocess_2, subprocess_payment)])
