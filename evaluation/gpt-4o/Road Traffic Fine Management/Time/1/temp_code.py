
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Combine 'Insert Fine Notification' and 'Add penalty' for concurrent execution
subprocess_0 = gen.partial_order(dependencies=[(insert_fine_notification,), (add_penalty,)])

# Simplify subprocess_1 by removing the loop as 'Payment' should ideally be a once-off activity
subprocess_1 = payment

# Streamline subprocess_3 by eliminating the redundant xor structure
subprocess_3 = gen.xor(send_for_credit_collection, subprocess_1)

# Simplify subprocess_2, removing unnecessary choices
subprocess_2 = subprocess_0

# Combine 'Send Fine' and subprocess_2 directly for concurrent execution
subprocess_4 = gen.partial_order(dependencies=[(send_fine,), (subprocess_2,)])

# Eliminate subprocess_5 and combine directly since the choice is redundant.
# These changes ensure non-dependent subprocesses run concurrently, or choices are direct. 
final_model = gen.partial_order(dependencies = [(create_fine,), (subprocess_4,), (subprocess_3,)])
