from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New activities for validation, delivery, reminders, appeal, and checks
validate_evidence = gen.activity('Validate Evidence')
check_duplicate = gen.activity('Check Duplicate/Existing Fine')
validate_debtor_data = gen.activity('Validate Debtor Data')
send_e_fine = gen.activity('Send e-Fine')
wait_due_date = gen.activity('Wait for Due Date')
send_final_reminder = gen.activity('Send Final Reminder')
record_appeal = gen.activity('Record Appeal')
review_appeal = gen.activity('Review Appeal')
cancel_fine = gen.activity('Cancel Fine')
final_collection_check = gen.activity('Final Collection Eligibility Check')

# Submodels
# Digital-first delivery choice (mandatory delivery)
delivery_choice = gen.xor(send_e_fine, send_fine)

# Appeal path: optional appeal -> review -> optionally cancel
appeal_resolution = gen.xor(None, cancel_fine)
appeal_process = gen.partial_order(dependencies=[(record_appeal, review_appeal), (review_appeal, appeal_resolution)])
appeal_branch = gen.xor(None, appeal_process)

# Payment path: optional, supports 1..n payments
payment_loop = gen.loop(payment, None)
payment_path = gen.xor(None, payment_loop)

# Penalty is optional after reminders
penalty_xor = gen.xor(None, add_penalty)

# Optional collection after final eligibility check
collection_choice = gen.xor(None, send_for_credit_collection)

# Final model: enforce proper sequencing and gates
final_model = gen.partial_order(
    dependencies=[
        (validate_evidence, check_duplicate),
        (check_duplicate, validate_debtor_data),
        (validate_debtor_data, create_fine),
        (create_fine, delivery_choice),
        (delivery_choice, insert_fine_notification),
        (insert_fine_notification, wait_due_date),
        (wait_due_date, send_final_reminder),
        (send_final_reminder, penalty_xor),
        (delivery_choice, appeal_branch),
        (delivery_choice, payment_path),
        (penalty_xor, final_collection_check),
        (appeal_branch, final_collection_check),
        (payment_path, final_collection_check),
        (final_collection_check, collection_choice),
    ]
)