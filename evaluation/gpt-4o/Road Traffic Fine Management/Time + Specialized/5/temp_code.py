
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

# New activities for improvement
verify_fine = gen.activity('Verify Fine')

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add Penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Adjusting subprocesses for efficiency
subprocess_c = gen.xor(None, verify_fine)  # Optional verification step

subprocess_0 = gen.xor(None, gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)]))  # Make notification optional
subprocess_1 = gen.loop(payment, None) 
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(None, send_for_credit_collection, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(send_fine, subprocess_2)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(subprocess_c, create_fine), (create_fine, subprocess_5), (subprocess_5, subprocess_3)]) 
