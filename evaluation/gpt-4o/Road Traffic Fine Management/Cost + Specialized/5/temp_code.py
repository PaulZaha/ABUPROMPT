
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

automated_validation = gen.activity('Automated Validation')

create_fine = gen.partial_order(dependencies=[(automated_validation, gen.activity('Create Fine'))])
send_fine = gen.activity('Send Fine')
insert_notification_penalty = gen.activity('Insert Notification and Add Penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(send_fine, insert_notification_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, subprocess_0)

verification_before_collection = gen.activity('Verification before Credit Collection')
subprocess_3 = gen.partial_order(dependencies = [(verification_before_collection, send_for_credit_collection)])

verify_and_prepare_payment = gen.xor(None, subprocess_1)

final_model = gen.partial_order(dependencies = [
    (create_fine, subprocess_2),
    (subprocess_2, verify_and_prepare_payment),
    (verify_and_prepare_payment, subprocess_3)
])
