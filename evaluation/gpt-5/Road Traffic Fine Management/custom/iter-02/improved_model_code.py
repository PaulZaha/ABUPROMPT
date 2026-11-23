from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# New/repurposed activities to prevent false fines
validate_fine_data = gen.activity('Validate Fine Data')
validate_recipient = gen.activity('Validate Recipient')
check_duplicate_paid = gen.activity('Check Duplicate/Already Paid')
manual_review = gen.activity('Manual Review')
approve_fine = gen.activity('Approve Fine for Sending')
cancel_fine = gen.activity('Cancel Fine')

# Send path: validations + optional manual review + approval + sending + post-send actions
vfd_send = validate_fine_data.copy()
vr_send = validate_recipient.copy()
cd_send = check_duplicate_paid.copy()
mr_send_opt = gen.xor(None, manual_review.copy())
payment_loop = gen.loop(payment, None)
penalty_opt = gen.xor(None, add_penalty)
collection_opt = gen.xor(None, send_for_credit_collection)

send_path = gen.partial_order(dependencies=[
    (vfd_send, approve_fine),
    (vr_send, approve_fine),
    (cd_send, approve_fine),
    (mr_send_opt, approve_fine),
    (approve_fine, insert_fine_notification),
    (insert_fine_notification, send_fine),
    (send_fine, payment_loop),
    (payment_loop, penalty_opt),
    (penalty_opt, collection_opt)
])

# Cancel path: validations + optional manual review -> cancel fine
vfd_cancel = validate_fine_data.copy()
vr_cancel = validate_recipient.copy()
cd_cancel = check_duplicate_paid.copy()
mr_cancel_opt = gen.xor(None, manual_review.copy())

cancel_path = gen.partial_order(dependencies=[
    (vfd_cancel, cancel_fine),
    (vr_cancel, cancel_fine),
    (cd_cancel, cancel_fine),
    (mr_cancel_opt, cancel_fine)
])

# Decision: either cancel (invalid) or proceed to send (valid)
decision = gen.xor(cancel_path, send_path)

final_model = gen.partial_order(dependencies=[
    (create_fine, decision)
])