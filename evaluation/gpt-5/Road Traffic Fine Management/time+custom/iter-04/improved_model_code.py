from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
verify_fine = gen.activity('Verify Fine (auto + manual for flagged)')
insert_fine_notification = gen.activity('Insert Fine Notification')
prepare_payment_link = gen.activity('Prepare Digital Payment Link')
send_fine = gen.activity('Send Fine')
check_due_payment = gen.activity('Check Due Date & Payment Status')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')
reject_fine = gen.activity('Reject Fine')

# Penalty is only applied if the due date has passed and payment was not recorded
penalty_decision = gen.xor(None, add_penalty)

# If unpaid after send, check status, optionally add penalty, then escalate to collections
non_payment_path = gen.partial_order(dependencies=[
    (check_due_payment, penalty_decision),
    (penalty_decision, send_for_credit_collection)
])

# After sending, either payment is received or proceed to the non-payment handling path
post_send_branch = gen.xor(payment, non_payment_path)

# Validated path: verify, then prepare in parallel (notification + payment link), then send, then follow-up
valid_path = gen.partial_order(dependencies=[
    (verify_fine, insert_fine_notification),
    (verify_fine, prepare_payment_link),
    (insert_fine_notification, send_fine),
    (prepare_payment_link, send_fine),
    (send_fine, post_send_branch)
])

# If validation fails, reject and terminate; otherwise continue with the validated path
main_xor = gen.xor(valid_path, reject_fine)

final_model = gen.partial_order(dependencies=[(create_fine, main_xor)] )