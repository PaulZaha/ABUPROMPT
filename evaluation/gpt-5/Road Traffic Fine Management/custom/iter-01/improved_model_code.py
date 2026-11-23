from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New pre-send validation and approval activities
validate_recipient = gen.activity('Validate Recipient Data')
verify_evidence = gen.activity('Verify Violation Evidence')
duplicate_check = gen.activity('Duplicate Check')
check_waiver = gen.activity('Check Waiver/Prior Payment')
approve_to_send = gen.activity('Approve Fine to Send')
correct_fine = gen.activity('Correct Fine Data')
cancel_fine = gen.activity('Cancel Fine')

# Pre-send concurrent validations and approval gate
pre_send_po = gen.partial_order(dependencies=[
    (create_fine, validate_recipient),
    (create_fine, verify_evidence),
    (create_fine, duplicate_check),
    (create_fine, check_waiver),
    (validate_recipient, approve_to_send),
    (verify_evidence, approve_to_send),
    (duplicate_check, approve_to_send),
    (check_waiver, approve_to_send)
])

# Allow correction and re-validation before any send decision
pre_send_loop = gen.loop(pre_send_po, correct_fine)

# Post-send settlement and escalation
payment_loop = gen.loop(None, payment)  # Payments can occur 0..n times
penalty_then_collection = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])
escalation_xor = gen.xor(None, penalty_then_collection)

send_path = gen.partial_order(dependencies=[
    (send_fine, insert_fine_notification),
    (insert_fine_notification, payment_loop),
    (payment_loop, escalation_xor)
])

# Decision: send approved fine or cancel
decision = gen.xor(send_path, cancel_fine)

# Final model: validations/approval loop must complete before decision to send or cancel
final_model = gen.partial_order(dependencies=[(pre_send_loop, decision)])