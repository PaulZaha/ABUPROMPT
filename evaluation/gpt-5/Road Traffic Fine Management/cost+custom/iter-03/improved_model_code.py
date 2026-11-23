from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New/augmented control activities for quality gates and cost control
validate_fine = gen.activity('Validate Fine (rules+dedup)')
verify_identity = gen.activity('Verify Identity & Address')
manual_review = gen.activity('Manual Review if Flagged')
cancel_fine = gen.activity('Cancel Fine')
pre_collection_check = gen.activity('Pre-collection Payment/Dispute Check')

# Optional manual review if the automated checks flag a risk
maybe_manual_review = gen.xor(None, manual_review)

# Payment can occur 0..n times (optional installments/partial payments)
payment_loop = gen.loop(None, payment)

# Only send to collections if check passes (optional)
maybe_send_to_collection = gen.xor(None, send_for_credit_collection)

# Continue path (valid fines)
continue_path = gen.partial_order(dependencies=[
    (create_fine, validate_fine),
    (validate_fine, verify_identity),
    (verify_identity, maybe_manual_review),
    (maybe_manual_review, send_fine),
    (send_fine, insert_fine_notification),
    (insert_fine_notification, add_penalty),
    (send_fine, payment_loop),
    (add_penalty, pre_collection_check),
    (pre_collection_check, maybe_send_to_collection)
])

# Cancel path (invalid/flagged fines) - use copies to avoid node sharing across XOR branches
create_fine_c = create_fine.copy()
validate_fine_c = validate_fine.copy()
verify_identity_c = verify_identity.copy()
maybe_manual_review_c = maybe_manual_review.copy()

cancel_path = gen.partial_order(dependencies=[
    (create_fine_c, validate_fine_c),
    (validate_fine_c, verify_identity_c),
    (verify_identity_c, maybe_manual_review_c),
    (maybe_manual_review_c, cancel_fine)
])

# Final model: either cancel the fine after validation or proceed with controlled, cost-aware settlement flow
final_model = gen.xor(cancel_path, continue_path)