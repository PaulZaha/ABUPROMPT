
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
verify_fine = gen.activity('Verify Fine')  # New verification activity
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Verification subprocess added before sending a fine
subprocess_verification = gen.xor(verify_fine, None)  # Now submodel is conditional on verification

subprocess_0 = gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(None, send_for_credit_collection, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(send_fine, subprocess_2)])
subprocess_5 = gen.xor(None, subprocess_4)

# Integrating the verification step in the existing process
final_model = gen.partial_order(dependencies = [
    (create_fine, subprocess_verification),  # Create fine followed by verification
    (subprocess_verification, subprocess_5), # Verification leads to sending fine or not
    (subprocess_5, subprocess_3)
])
