
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
verify_fine_data = gen.activity('Verify Fine Data')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.partial_order(dependencies = [(send_fine, subprocess_0)])  # Remove optionality
subprocess_3 = gen.xor(None, send_for_credit_collection, subprocess_1)
final_subprocess = gen.partial_order(dependencies = [(subprocess_2, subprocess_3)])  # Ensure verification step before credit collections

final_model = gen.partial_order(dependencies = [(create_fine, verify_fine_data), (verify_fine_data, final_subprocess)]) 
