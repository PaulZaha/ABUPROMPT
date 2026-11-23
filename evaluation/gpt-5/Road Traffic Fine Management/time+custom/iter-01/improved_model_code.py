from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities (existing)
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New control/quality activities to prevent false fines
auto_validate = gen.activity('Auto-Validate Fine Data')
verify_recipient = gen.activity('Verify Recipient Address')
check_duplicate = gen.activity('Check Duplicate Fine')
correct_fine_data = gen.activity('Correct Fine Data')
cancel_fine = gen.activity('Cancel Fine')

# Concurrent validations with corrective loop
validations_parallel = gen.partial_order(dependencies=[(auto_validate,), (verify_recipient,), (check_duplicate,)])
validation_loop = gen.loop(validations_parallel, correct_fine_data)

# Payment can occur one or more times when chosen
payment_loop = gen.loop(payment, None)

# Escalation path: only after non-payment, add penalty then send to credit collection
escalation = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])

# Exclusive post-send routing: either payments or escalation (not both)
payment_or_escalate = gen.xor(payment_loop, escalation)

# Send path: send and notify can run in parallel, both must complete before routing
send_branch = gen.partial_order(dependencies=[(send_fine, payment_or_escalate), (insert_fine_notification, payment_or_escalate)])

# Decide to cancel (invalid/duplicate) or proceed to send
proceed = gen.xor(cancel_fine, send_branch)

# End-to-end flow
final_model = gen.partial_order(dependencies=[(create_fine, validation_loop), (validation_loop, proceed)])