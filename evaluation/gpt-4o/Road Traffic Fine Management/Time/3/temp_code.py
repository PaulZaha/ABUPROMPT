
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies=[(insert_fine_notification,), (add_penalty,)])  # concurrent execution of notifications and penalties
subprocess_1 = gen.xor(payment, None)  # optional payment step, simplifying structured payments
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.partial_order(dependencies=[(send_for_credit_collection, subprocess_1)])  # prioritize credit collection step after fines
subprocess_4 = gen.xor(None, send_fine, subprocess_2)  # make send_fine optional to prioritize time efficiency
subprocess_5 = gen.partial_order(dependencies=[(create_fine, subprocess_4), (subprocess_4, subprocess_3)])

final_model = subprocess_5
