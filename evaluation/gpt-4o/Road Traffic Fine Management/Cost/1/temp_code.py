
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_fine = gen.activity('Create Fine')
send_fine = gen.activity('Send Fine')
automated_insert_notification = gen.activity('Automated Insert Notification & Penalty')
send_for_credit_collection = gen.activity('Send for Credit Collection')
payment = gen.activity('Payment')

# Use a sequential process for creating fines and sending notifications
subprocess_0 = gen.partial_order(dependencies = [(create_fine, send_fine)])

# Loop through the payment process once, add credit collection if payment fails
payment_process = gen.loop(payment, None)  
subprocess_1 = gen.xor(payment_process, send_for_credit_collection) 

# Improved subprocess combining notification and penalty insertion
subprocess_2 = gen.xor(automated_insert_notification, None)

# Final model with optimized paths for cost reduction
final_model = gen.partial_order(dependencies = [(subprocess_0, subprocess_2), (subprocess_2, subprocess_1)]) 
