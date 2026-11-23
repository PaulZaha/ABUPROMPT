from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_fine = gen.activity('Create Fine')
validate_fine = gen.activity('Validate Fine Data')
cancel_fine = gen.activity('Cancel Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')
wait_due_date = gen.activity('Wait for Due Date')
check_payment_status_1 = gen.activity('Check Payment Status')
wait_grace_period = gen.activity('Wait Grace Period')
check_payment_status_2 = gen.activity('Check Payment Status (Post-Reminder)')
close_case = gen.activity('Close Case')

# Payment branch: at least one payment, then close the case
payment_loop = gen.loop(payment, None)
close_case_after_payment = close_case
payment_branch = gen.partial_order(dependencies=[(payment_loop, close_case_after_payment)])

# Escalation path after second check: add penalty then send to collection
escalate_to_collection = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])

# Reminder and post-reminder check
reminder_flow = gen.partial_order(dependencies=[
    (insert_fine_notification, wait_grace_period),
    (wait_grace_period, check_payment_status_2)
])
decision_after_second_check = gen.xor(close_case.copy(), escalate_to_collection)
post_reminder_path = gen.partial_order(dependencies=[(reminder_flow, decision_after_second_check)])

# Initial due-date wait and check
initial_check_flow = gen.partial_order(dependencies=[(wait_due_date, check_payment_status_1)])
decision_after_first_check = gen.xor(close_case.copy(), post_reminder_path)
overdue_branch = gen.partial_order(dependencies=[(initial_check_flow, decision_after_first_check)])

# After sending the fine, either payment occurs (and we close) or we go into the overdue branch
post_send_choice = gen.xor(payment_branch, overdue_branch)
proceed_path = gen.partial_order(dependencies=[(send_fine, post_send_choice)])

# Validation gate: either cancel the fine or proceed to send it
validation_decision = gen.xor(proceed_path, cancel_fine)

# Full process: create -> validate -> decide
final_model = gen.partial_order(dependencies=[(create_fine, validate_fine), (validate_fine, validation_decision)])