from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_fine = gen.activity('Create Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')

# New/augmented controls to reduce false fines and cost
auto_validate = gen.activity('Auto-Validate Fine Data')
check_exempt_dup = gen.activity('Check Exemptions and Duplicates')
validate_owner_address = gen.activity('Validate Owner and Address')
manual_review = gen.activity('Manual Review (If Flagged)')
cancel_fine = gen.activity('Cancel Fine')

# Channel optimization for cost
send_fine_digital = gen.activity('Send Fine (Digital)')
send_fine_postal = gen.activity('Send Fine (Postal)')

# Payment options (separate instances to avoid reuse conflicts)
payment_initial = gen.activity('Payment')
payment_after_penalty = gen.activity('Payment')

# Pre-collection gate to prevent false escalations
pre_collection_validation = gen.activity('Pre-Collection Validation')

# Optional manual review after automated checks
maybe_manual_review = gen.xor(None, manual_review)

# Choose lowest-cost channel by default (digital), with postal as fallback
send_choice = gen.xor(send_fine_digital, send_fine_postal)

# Pre-collection path enforces a final validation before collections
pre_to_collection = gen.partial_order(dependencies=[(pre_collection_validation, send_for_credit_collection)])

# After penalty, either accept payment or (after validation) escalate to collections
post_penalty_choice = gen.xor(payment_after_penalty, pre_to_collection)

# Escalation flow: reminder -> penalty -> then choose payment or collections
escalate_then_choice = gen.partial_order(dependencies=[
    (insert_fine_notification, add_penalty),
    (add_penalty, post_penalty_choice)
])

# After sending, either get payment or go through escalation
post_send_options = gen.xor(payment_initial, escalate_then_choice)

# Sending stage: choose channel, then proceed with post-send options
send_stage = gen.partial_order(dependencies=[(send_choice, post_send_options)])

# Decision after validation: cancel invalid fines or proceed to send
decision_model = gen.xor(cancel_fine, send_stage)

# Final model: validation chain -> decision
final_model = gen.partial_order(dependencies=[
    (create_fine, auto_validate),
    (auto_validate, check_exempt_dup),
    (check_exempt_dup, validate_owner_address),
    (validate_owner_address, maybe_manual_review),
    (maybe_manual_review, decision_model)
])