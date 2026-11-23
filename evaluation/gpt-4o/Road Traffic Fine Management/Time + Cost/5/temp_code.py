
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
handle_fine_notification = gen.activity('Handle Fine Notification')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = handle_fine_notification
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(send_for_credit_collection, payment)
subprocess_4 = gen.partial_order(dependencies = [(send_fine, subprocess_2)])
subprocess_5 = gen.xor(None, subprocess_4, subprocess_3)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_5)]) 
