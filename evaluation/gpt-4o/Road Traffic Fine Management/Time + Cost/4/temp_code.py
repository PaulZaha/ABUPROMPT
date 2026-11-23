
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(add_penalty,)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(subprocess_2, send_for_credit_collection, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(send_fine, insert_fine_notification)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_5), (subprocess_5, subprocess_3)]) 
