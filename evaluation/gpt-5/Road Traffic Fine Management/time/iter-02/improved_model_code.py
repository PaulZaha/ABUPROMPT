from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Payment-first with penalty-driven retries: first attempt immediately, penalties only before subsequent attempts
payment_cycle = gen.loop(payment, add_penalty)

# Resolve either by paying (possibly after penalties) or by escalation
resolution = gen.xor(payment_cycle, send_for_credit_collection)

# Run communication/recording in parallel with resolution immediately after creating the fine
final_model = gen.partial_order(dependencies=[
    (create_fine, send_fine),
    (create_fine, insert_fine_notification),
    (create_fine, resolution)
])