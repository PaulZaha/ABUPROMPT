from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_fine = gen.activity('Create Fine')
validate_fine = gen.activity('Validate Fine')
correct_fine_data = gen.activity('Correct Fine Data')
cancel_fine = gen.activity('Cancel Fine')

insert_fine_notification = gen.activity('Insert Fine Notification')
verify_recipient = gen.activity('Verify Recipient & Address')
send_fine = gen.activity('Send Fine')

payment = gen.activity('Payment')
evaluate_due_date = gen.activity('Evaluate Due Date')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')

# Validation and correction loop: validate first; every correction triggers another validation
validation_loop = gen.loop(validate_fine, correct_fine_data)

# Payment loop is optional (0..n) using XOR around a self-loop (1..n)
payment_loop = gen.loop(payment, None)
payment_optional = gen.xor(None, payment_loop)

# Penalty application is optional, only after due date evaluation
penalty_optional = gen.xor(None, add_penalty)

# Proceed-to-send path: pre-send tasks in parallel; send depends on both
# Post-send: payment can start; due date evaluation leads to optional penalty then credit collection
to_be_sent = gen.partial_order(dependencies=[
    (insert_fine_notification, send_fine),
    (verify_recipient, send_fine),
    (send_fine, payment_optional),
    (send_fine, evaluate_due_date),
    (evaluate_due_date, penalty_optional),
    (penalty_optional, send_for_credit_collection)
])

# Decision after validation: either cancel or proceed to send path
decision = gen.xor(cancel_fine, to_be_sent)

# Final model: create -> validate/correct -> decision (cancel vs proceed)
final_model = gen.partial_order(dependencies=[
    (create_fine, validation_loop),
    (validation_loop, decision)
])