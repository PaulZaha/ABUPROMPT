from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_fine = gen.activity('Create Fine')
send_fine_digital = gen.activity('Send Fine (Digital)')
notify_and_apply_penalty = gen.activity('Notify and Apply Penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Cap payment attempts to at most two (reduces repeated transaction/handling costs)
payment_attempt1 = payment
payment_attempt2_a = payment.copy()
payment_attempt2_b = payment.copy()

two_payment_attempts = gen.partial_order(dependencies=[(payment_attempt2_a, payment_attempt2_b)])
capped_payment_attempts = gen.xor(payment_attempt1, two_payment_attempts)

# Escalation only after payment attempts; combine notification and penalty into one step
escalation_subprocess = gen.partial_order(dependencies=[(notify_and_apply_penalty, send_for_credit_collection)])
optional_escalation = gen.xor(None, escalation_subprocess)

# Payment path: capped attempts followed by optional escalation
payment_path = gen.partial_order(dependencies=[(capped_payment_attempts, optional_escalation)])

# Optional digital sending to avoid postage/print on cancellations
send_fine_optional = gen.xor(None, send_fine_digital)

# After creating the fine, optionally send it digitally, then either end or go through the payment path
process_choice = gen.xor(None, payment_path)

final_model = gen.partial_order(dependencies=[(create_fine, send_fine_optional), (send_fine_optional, process_choice)])