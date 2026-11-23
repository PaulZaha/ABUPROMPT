
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Changed subprocess_0 to execute activities concurrently
subprocess_0 = gen.partial_order(dependencies=[(insert_fine_notification,), (add_penalty,)])

# Optimized subprocess_1 loop by marking payment as optional if successful
subprocess_1 = gen.loop(None, payment) 

# Simplified subprocess_2 to eliminate redundant choices
subprocess_2 = subprocess_0 

# Consolidated subprocess_3 with subprocess_1 for better flow
subprocess_3 = gen.xor(subprocess_1, send_for_credit_collection)

# Streamlined subprocess_4 for concurrency with send_fine task
subprocess_4 = gen.partial_order(dependencies=[(send_fine, subprocess_2)])

# Removed unnecessary optional subprocess choice in subprocess_5
subprocess_5 = subprocess_4 

final_model = gen.partial_order(dependencies=[(create_fine, subprocess_5), (subprocess_5, subprocess_3)])
