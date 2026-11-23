
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
notify_and_add_penalty = gen.activity('Notify and Add Penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Combine 'Insert Fine Notification' and 'Add penalty' into one streamlined activity
subprocess_0 = gen.xor(None, notify_and_add_penalty)
subprocess_1 = gen.loop(payment, None)

# Use xor to define credit collection as a more explicitly optional step
subprocess_3 = gen.xor(subprocess_1, send_for_credit_collection)
subprocess_4 = gen.partial_order(dependencies = [(send_fine, subprocess_0)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_5), (subprocess_5, subprocess_3)])
