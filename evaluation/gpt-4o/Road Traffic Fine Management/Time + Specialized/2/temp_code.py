
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Optimized subprocess showcasing dependencies and logical groups
subprocess_payment_check = gen.xor(payment, gen.xor(None, send_for_credit_collection))
subprocess_fines_and_notifications = gen.partial_order(dependencies=[(send_fine, insert_fine_notification)])

# Merge subprocesses where fitting and make logical pathways
subprocess_notifications_and_penalties = gen.partial_order(dependencies=[(subprocess_fines_and_notifications, add_penalty)])

# final model refined
final_model = gen.partial_order(dependencies=[
    (create_fine, subprocess_payment_check), 
    (subprocess_payment_check, subprocess_notifications_and_penalties)
])
