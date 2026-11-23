from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New/auxiliary activities for quality and timing
auto_validate = gen.activity('Auto-Validate Fine Data')
manual_review = gen.activity('Manual Review (If Flagged)')
correct_fine = gen.activity('Correct Fine Data')
approve_send = gen.activity('Approve Fine For Sending')
cancel_fine = gen.activity('Cancel Fine')
wait_due = gen.activity('Wait Until Due Date')

# Distinct payment opportunities (to avoid an unbounded payment loop)
payment_pre_due = payment.copy()
payment_post_penalty = payment.copy()

# Validation loop (automated checks with optional manual correction cycles)
prepare_do = auto_validate
prepare_redo = gen.partial_order(dependencies=[(manual_review, correct_fine)])
prepare_loop = gen.loop(prepare_do, prepare_redo)

# Post-sending paths
post_penalty_xor = gen.xor(payment_post_penalty, send_for_credit_collection)
penalty_path = gen.partial_order(dependencies=[(add_penalty, post_penalty_xor)])

pre_penalty_xor = gen.xor(payment_pre_due, penalty_path)
rest_path = gen.partial_order(dependencies=[(insert_fine_notification, wait_due), (wait_due, pre_penalty_xor)])

after_send_xor = gen.xor(payment, rest_path)

# Approved branch: approve -> send -> handle payment/reminder/penalty/collection
approved_branch = gen.partial_order(dependencies=[(approve_send, send_fine), (send_fine, after_send_xor)])

# Decision: cancel vs approved branch
decision_xor = gen.xor(cancel_fine, approved_branch)

# Final model: create -> validate loop -> decision
final_model = gen.partial_order(dependencies=[(create_fine, prepare_loop), (prepare_loop, decision_xor)])