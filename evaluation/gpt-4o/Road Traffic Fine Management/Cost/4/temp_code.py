
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_and_add_penalty = gen.activity('Insert Notification with Penalty')
send_for_credit_collection = gen.activity('Automated Send for Credit Collection')  # Improved naming for clarity, assuming automation
payment = gen.activity('Payment')

# Combine insert_fine_notification and add_penalty into a single activity.
subprocess_0 = gen.activity('Insert Notification with Penalty')

# Optimize subprocess_0 within xor for conditional execution.
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(None, send_for_credit_collection, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(send_fine, subprocess_2)])
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_5), (subprocess_5, subprocess_3)])
