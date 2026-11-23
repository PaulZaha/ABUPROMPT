from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_fine = gen.activity('Create Fine')

# Pre-send automated checks (sequential gate)
automated_validation = gen.activity('Automated Validation')
check_duplicate = gen.activity('Check Duplicate')
sync_recent_payments = gen.activity('Sync Recent Payments')
check_permits = gen.activity('Check Permits/Exemptions')

# Approval and review controls
manual_review = gen.activity('Manual Review (4-Eyes)')
approve_to_send = gen.activity('Approve to Send')
cancel_fine = gen.activity('Cancel Fine')

# Preparation and sending
generate_evidence = gen.activity('Generate Evidence Package')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')

# Post-send actions
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Post-send options after a fine is sent
payment_loop = gen.loop(payment, None)
post_send_auto = gen.xor(None, send_for_credit_collection, payment_loop)

# Auto-approved path: approval -> prepare -> insert -> send -> (payment/collections); penalty only after proper insertion
auto_approved_branch = gen.partial_order(dependencies=[
    (approve_to_send, generate_evidence),
    (generate_evidence, insert_fine_notification),
    (insert_fine_notification, send_fine),
    (send_fine, post_send_auto),
    (insert_fine_notification, add_penalty)
])

# Manual-review path uses copies to keep branches disjoint
approve_to_send_m = approve_to_send.copy()
generate_evidence_m = generate_evidence.copy()
insert_fine_notification_m = insert_fine_notification.copy()
send_fine_m = send_fine.copy()
add_penalty_m = add_penalty.copy()
send_for_credit_collection_m = send_for_credit_collection.copy()
payment_m = payment.copy()
payment_loop_m = gen.loop(payment_m, None)
post_send_manual = gen.xor(None, send_for_credit_collection_m, payment_loop_m)

manual_review_branch = gen.partial_order(dependencies=[
    (manual_review, approve_to_send_m),
    (approve_to_send_m, generate_evidence_m),
    (generate_evidence_m, insert_fine_notification_m),
    (insert_fine_notification_m, send_fine_m),
    (send_fine_m, post_send_manual),
    (insert_fine_notification_m, add_penalty_m)
])

# Decision after prechecks: cancel, manual-review-and-approve, or auto-approve-and-send
decision_xor = gen.xor(
    cancel_fine,
    manual_review_branch,
    auto_approved_branch
)

# Top-level sequencing: create -> all prechecks -> decision/approval -> (send or cancel)
final_model = gen.partial_order(dependencies=[
    (create_fine, automated_validation),
    (automated_validation, check_duplicate),
    (check_duplicate, sync_recent_payments),
    (sync_recent_payments, check_permits),
    (check_permits, decision_xor)
])