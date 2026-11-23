
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_notification_and_penalty = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])
subprocess_payment_loop = gen.loop(payment, None)
subprocess_credit_collection_concurrent = gen.partial_order(dependencies=[(send_for_credit_collection,), (subprocess_payment_loop,)])

subprocess_review_before_send = gen.xor(subprocess_notification_and_penalty, None)
subprocess_send_fine = gen.partial_order(dependencies=[(send_fine, subprocess_review_before_send)])

final_model = gen.partial_order(dependencies=[
    (create_fine, subprocess_send_fine), 
    (subprocess_send_fine, subprocess_credit_collection_concurrent)
]) 
