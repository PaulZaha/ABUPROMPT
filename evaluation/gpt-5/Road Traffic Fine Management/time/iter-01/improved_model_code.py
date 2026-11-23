from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Run Send Fine and Insert Fine Notification in parallel (when needed)
send_and_notify = gen.partial_order(dependencies=[(send_fine,), (insert_fine_notification,)])
opt_send_and_notify = gen.xor(None, send_and_notify)

# Credit collection path: add penalty then send for credit collection
credit_collection_path = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])

# Settlement decision: either skip, take payment, or escalate to credit collection
settlement_choice = gen.xor(None, payment, credit_collection_path)

# After creating the fine, (optionally) send/notify can proceed in parallel with settlement
final_model = gen.partial_order(dependencies=[(create_fine, opt_send_and_notify), (create_fine, settlement_choice)])