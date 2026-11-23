
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine_and_notify = gen.activity('Send Fine and Insert Notification')  # Merged send and notify steps
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(send_fine_and_notify, add_penalty)]) # Optimized merged task
subprocess_1 = gen.xor(None, send_for_credit_collection) # Changed subprocess_1 to an optional step
subprocess_2 = gen.loop(payment, None)  # Limit impacts by creating no repetitive loop around payment step
subprocess_3 = gen.partial_order(dependencies = [(subprocess_0, subprocess_1)])

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_3), (subprocess_3, subprocess_2)]) 
