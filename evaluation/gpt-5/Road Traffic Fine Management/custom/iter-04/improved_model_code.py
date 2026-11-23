from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New activities to reduce falsely sent fines
validate_violation_data = gen.activity('Validate Violation Data')
check_exemptions_permits = gen.activity('Check Exemptions and Permits')
check_duplicates_payments = gen.activity('Check Duplicates/Existing Payments')
verify_contact_details = gen.activity('Verify Contact Details')
manual_review = gen.activity('Manual Review (if ambiguous)')
approve_fine = gen.activity('Approve Fine for Sending')
cancel_fine = gen.activity('Cancel Fine')

# Pre-send validation sequence
validation_seq = gen.partial_order(dependencies=[
    (validate_violation_data, check_exemptions_permits),
    (check_exemptions_permits, check_duplicates_payments),
    (check_duplicates_payments, verify_contact_details)
])

# Optional manual review before approval
optional_manual_review = gen.xor(None, manual_review)

# Optional notification after sending
optional_insert_notification = gen.xor(None, insert_fine_notification)

# Payment loop (can attempt payment multiple times)
payment_loop = gen.loop(payment, None)

# Credit collection only after penalty has been added
credit_path = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])

# Post-send choices: none, payment attempts, or escalate after penalty
post_send_choice = gen.xor(None, payment_loop, credit_path)

# Approve branch: review (optional) -> approve -> send -> optional notify -> post-send handling
approve_branch = gen.partial_order(dependencies=[
    (optional_manual_review, approve_fine),
    (approve_fine, send_fine),
    (send_fine, optional_insert_notification),
    (optional_insert_notification, post_send_choice)
])

# Decision: either proceed to approved sending flow or cancel fine
decision_xor = gen.xor(approve_branch, cancel_fine)

# Overall process: create -> validate -> decide (approve/send or cancel)
final_model = gen.partial_order(dependencies=[
    (create_fine, validation_seq),
    (validation_seq, decision_xor)
])