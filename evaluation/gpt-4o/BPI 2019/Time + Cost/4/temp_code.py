
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

subprocess_1 = vendor_creates_invoice  # Removed XOR making invoicing mandatory
subprocess_2 = remove_payment_block  # Direct activity without XOR, assuming payment block removal is needed.
subprocess_3 = gen.partial_order(dependencies=[(record_goods_receipt, subprocess_1)])  # Consider concurrency
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt,), (subprocess_2, clear_invoice)])  # Removed unnecessary XOR

final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, receive_order_confirmation),  # Concurrent start
    (receive_order_confirmation, subprocess_3),  # Moves after receive order
    (subprocess_3, subprocess_4)  # Efficient parallelization assumed for further processing post goods receipt
]) 
