
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Subprocess 0 and 5 adjusted for concurrency where sequential dependency is non-strict
subprocess_0_5 = gen.partial_order(dependencies=[(send_fine,), (insert_fine_notification,), (add_penalty,)])

# Payment self-loop remains as is but simplified with subprocesses
subprocess_1 = gen.loop(payment, None)

# Combine and streamline conditional and parallel subprocess handling
subprocess_2_3 = gen.xor(None, subprocess_0_5, send_for_credit_collection, subprocess_1)

# Restructure main model to reduce nested conditionals and maximize concurrency
final_model = gen.partial_order(dependencies=[(create_fine, subprocess_2_3)])
