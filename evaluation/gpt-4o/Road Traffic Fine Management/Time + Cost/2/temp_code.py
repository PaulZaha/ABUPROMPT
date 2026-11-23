
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(insert_fine_notification, ), (add_penalty, )])  # Concurrent execution

# Streamlining payment process to make it a single attempt followed by possible credit collection
payment_collection_process = gen.xor(payment, send_for_credit_collection) 

subprocess_3 = gen.xor(None, payment_collection_process)  # Making payment and credit collection a direct choice

# Eliminating unnecessary subprocess_2 as notifications are now concurrent with penalties:
subprocess_4 = gen.partial_order(dependencies = [(send_fine, subprocess_0)])  # Concurrent notification and penalty

subprocess_5 = gen.xor(None, subprocess_4)  # Optional sending of fine

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_5), (subprocess_5, subprocess_3)]) 
