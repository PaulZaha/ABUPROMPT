
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Modified to increase concurrency
subprocess_0 = gen.partial_order(dependencies=[create_purchase_order_item, receive_order_confirmation])
subprocess_1 = gen.partial_order(dependencies=[vendor_creates_invoice, record_goods_receipt])
subprocess_2 = gen.xor(None, remove_payment_block)

subprocess_3 = gen.partial_order(dependencies=[(record_invoice_receipt, subprocess_2), (subprocess_2, clear_invoice)])
subprocess_4 = gen.xor(None, subprocess_3)

# New concurrency setup with reduced dependencies
final_model = gen.partial_order(dependencies=[(subprocess_0, subprocess_1), (subprocess_1, subprocess_4)])
