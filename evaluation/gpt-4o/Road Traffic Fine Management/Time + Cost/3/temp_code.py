
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Activity ordering and dependencies strengthened
subprocess_0 = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = subprocess_0  # Removed optional subprocess to ensure penalties are added invariably
subprocess_3 = gen.partial_order(dependencies=[(send_for_credit_collection, subprocess_1)])  # Ensure credit collection occurs before payment or loop
subprocess_4 = gen.partial_order(dependencies=[(send_fine, subprocess_2)])
subprocess_5 = subprocess_4  # Removed optional step to make subprocess_4 mandatory

final_model = gen.partial_order(dependencies=[(create_fine, subprocess_5), (subprocess_5, subprocess_3)])
