
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
verify_order_uniqueness = gen.activity('Verify Order Uniqueness')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Introducing verification after order creation
subprocess_0 = gen.partial_order(dependencies=[(create_purchase_order_item, verify_order_uniqueness)])

subprocess_1a = gen.partial_order(dependencies=[(subprocess_0, receive_order_confirmation)])
subprocess_1b = gen.xor(None, vendor_creates_invoice)
subprocess_2 = gen.xor(None, remove_payment_block)

subprocess_3 = gen.partial_order(dependencies=[(record_goods_receipt,), (subprocess_1b,)])
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt, subprocess_2), (subprocess_2, clear_invoice)])
subprocess_5 = gen.xor(None, subprocess_4)

# Ensuring strong verification pathway and sequential order
final_model = gen.partial_order(dependencies=[(subprocess_1a, subprocess_3), (subprocess_3, subprocess_5)]) 
