
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
validate_fine = gen.activity('Validate Fine')  # New activity for fine validation
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.partial_order(dependencies=[(send_for_credit_collection,), (subprocess_1,)])  # Concurring send for credit collection and payment loop
subprocess_4 = gen.partial_order(dependencies = [(validate_fine, send_fine, subprocess_2)])  # Ensure validation before sending fines
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_5), (subprocess_5, subprocess_3)]) 