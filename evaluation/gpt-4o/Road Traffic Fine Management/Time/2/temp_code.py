
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Optimize subprocess by including parallel execution of insert notification and penalty
subprocess_optimized = gen.partial_order(dependencies=[
    (insert_fine_notification,), 
    (add_penalty,)
])

# Parallel execution of send_fine, subprocess_optimized and direct integration of send for credit collection
send_and_notify = gen.partial_order(dependencies=[
    (send_fine, subprocess_optimized),
    (send_for_credit_collection,)
])

# Simplified subprocess for payment, removing loop as it causes potential delay
final_model = gen.partial_order(dependencies=[
    (create_fine, send_and_notify),
    (payment,)
])
