
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Make 'Add penalty' optional to reduce unnecessary execution costs
subprocess_0 = gen.xor(None, gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)]))

# Parallelize 'Send for Credit Collection' and 'Payment' to reduce execution cost and time
subprocess_1 = gen.partial_order(dependencies = [(send_for_credit_collection,), (payment,)])

# Create partial orders for subprocesses to minimize overhead and remove redundant paths
subprocess_2 = gen.partial_order(dependencies = [(send_fine, subprocess_0)])
subprocess_3 = gen.xor(None, subprocess_2)

# Final model with optimized subprocesses
final_model = gen.partial_order(dependencies = [(create_fine, subprocess_3), (subprocess_3, subprocess_1)]) 
