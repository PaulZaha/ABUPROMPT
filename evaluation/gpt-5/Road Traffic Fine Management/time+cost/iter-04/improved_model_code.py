from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# If payment does not occur, apply penalty and send to credit collection
escalate = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])
post_choice = gen.xor(payment, escalate)

final_model = gen.partial_order(dependencies=[
    (create_fine, send_fine),
    (create_fine, insert_fine_notification),
    (send_fine, post_choice),
    (insert_fine_notification, post_choice)
])