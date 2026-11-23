from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New pre-dispatch validation and control steps
validate_violation_data = gen.activity('Validate Violation Data')
cross_check_registration = gen.activity('Cross-check Registration')
duplicate_fine_check = gen.activity('Duplicate Fine Check')
check_exemptions = gen.activity('Check Exemptions and Permits')
validate_contact_address = gen.activity('Validate Contact Address')
check_existing_payment = gen.activity('Check Existing Payment')
manual_review = gen.activity('Manual Review')
correct_fine_data = gen.activity('Correct Fine Data')
officer_confirmation = gen.activity('Issuing Officer Confirmation')
approve_dispatch = gen.activity('Approve Fine Dispatch')
cancel_fine = gen.activity('Cancel Fine')

# Concurrent automated validations
pre_validation = gen.partial_order(dependencies=[
    (validate_violation_data,),
    (cross_check_registration,),
    (duplicate_fine_check,),
    (check_exemptions,),
    (validate_contact_address,),
    (check_existing_payment,)
])

# Optional manual review and correction chain
review_chain = gen.partial_order(dependencies=[(manual_review, correct_fine_data), (correct_fine_data, officer_confirmation)])
manual_opt = gen.xor(None, review_chain)

# Post-send optional notification and penalty
notification_penalty = gen.partial_order(dependencies=[(insert_fine_notification, add_penalty)])
post_send_optional = gen.xor(None, notification_penalty)

# Payment handling and escalation
payment_loop = gen.loop(payment, None)
resolution = gen.xor(payment_loop, send_for_credit_collection)

# Approval gate and send branch (send only after explicit approval)
approval_and_send_branch = gen.partial_order(dependencies=[
    (approve_dispatch, send_fine),
    (send_fine, post_send_optional),
    (post_send_optional, resolution)
])

# Decision: approve and send vs. cancel (prevents sending when issues found)
decision = gen.xor(approval_and_send_branch, cancel_fine)

# Final process structure
final_model = gen.partial_order(dependencies=[
    (create_fine, pre_validation),
    (pre_validation, manual_opt),
    (manual_opt, decision)
])