
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
validate_fine = gen.activity('Validate Fine')  # Added validation step
approve_fine = gen.activity('Approve Fine')    # Added approval step
send_fine = gen.activity('Send Fine')
insert_fine_notification = gen.activity('Insert Fine Notification')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

subprocess_0 = gen.partial_order(dependencies = [(insert_fine_notification, add_penalty)])
subprocess_1 = gen.loop(payment, None)
subprocess_2 = gen.xor(None, subprocess_0)
subprocess_3 = gen.xor(None, send_for_credit_collection, subprocess_1)
subprocess_4 = gen.partial_order(dependencies = [(validate_fine, approve_fine)]) # submodel for validation and approval
subprocess_5 = gen.partial_order(dependencies = [(subprocess_4, send_fine)]) # send fine after approval
subprocess_6 = gen.xor(None, subprocess_5, subprocess_2) # Optional send fine 
subprocess_7 = gen.xor(None, subprocess_6)

final_model = gen.partial_order(dependencies = [(create_fine, subprocess_7), (subprocess_7, subprocess_3)])
