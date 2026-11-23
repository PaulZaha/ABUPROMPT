from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
add_penalty = gen.activity('Add penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

non_payment_path = gen.partial_order(dependencies=[(add_penalty, send_for_credit_collection)])
decision = gen.xor(payment, non_payment_path)

final_model = gen.partial_order(dependencies=[(create_fine, send_fine), (send_fine, decision)])