from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New/improved control activities
validate_fine_data = gen.activity('Validate Fine Data')
check_violation_evidence = gen.activity('Check Violation Evidence')
check_duplicate_fine = gen.activity('Check Duplicate Fine')
approve_fine = gen.activity('Approve Fine')
cancel_fine = gen.activity('Cancel Fine')
send_payment_reminder = gen.activity('Send Payment Reminder')
reconcile_payment = gen.activity('Reconcile Payment')
check_payment_overdue = gen.activity('Check Payment Overdue')

# Payment handling: retry with reminders
payment_loop = gen.loop(payment, send_payment_reminder)

# Overdue/escalation path only if unpaid
overdue_path = gen.partial_order(dependencies=[
    (check_payment_overdue, add_penalty),
    (add_penalty, send_for_credit_collection)
])

# Close when paid, or escalate if overdue
paid_vs_overdue = gen.xor(reconcile_payment, overdue_path)

# Valid fines are sent, recorded, then go through payment handling
send_flow = gen.partial_order(dependencies=[
    (send_fine, insert_fine_notification),
    (insert_fine_notification, payment_loop),
    (payment_loop, paid_vs_overdue)
])

# Decision: cancel invalid fines or proceed with send/payment
send_or_cancel = gen.xor(cancel_fine, send_flow)

# Top-level flow with parallel validations and approval gate
final_model = gen.partial_order(dependencies=[
    (create_fine, validate_fine_data),
    (create_fine, check_violation_evidence),
    (create_fine, check_duplicate_fine),
    (validate_fine_data, approve_fine),
    (check_violation_evidence, approve_fine),
    (check_duplicate_fine, approve_fine),
    (approve_fine, send_or_cancel)
])