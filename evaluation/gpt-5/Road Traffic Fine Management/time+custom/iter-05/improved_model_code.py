from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')

validate_fine_data = gen.activity('Validate Fine Data')
verify_recipient = gen.activity('Verify Recipient & Address')
check_duplicate = gen.activity('Check Duplicate / Prior Payment')

manual_review = gen.activity('Manual Review (Flagged)')
cancel_fine = gen.activity('Cancel Fine')

send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')

send_reminder = gen.activity('Send Payment Reminder')
payment = gen.activity('Payment')
add_penalty = gen.activity('Add penalty')
check_credit_eligibility = gen.activity('Check Credit Collection Eligibility')
send_for_credit_collection = gen.activity('Send for Credit Collection')

manual_review_optional = gen.xor(None, manual_review)

payment_loop = gen.loop(None, payment)
reminder_loop = gen.loop(None, send_reminder)
credit_decision = gen.xor(None, send_for_credit_collection)

send_path = gen.partial_order(dependencies=[
    (send_fine, insert_fine_notification),
    (insert_fine_notification, payment_loop),
    (insert_fine_notification, reminder_loop),
    (payment_loop, add_penalty),
    (reminder_loop, add_penalty),
    (add_penalty, check_credit_eligibility),
    (check_credit_eligibility, credit_decision)
])

decision_xor = gen.xor(send_path, cancel_fine)

final_model = gen.partial_order(dependencies=[
    (create_fine, validate_fine_data),
    (create_fine, verify_recipient),
    (create_fine, check_duplicate),
    (validate_fine_data, manual_review_optional),
    (verify_recipient, manual_review_optional),
    (check_duplicate, manual_review_optional),
    (manual_review_optional, decision_xor)
])