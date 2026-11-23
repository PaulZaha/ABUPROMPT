
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')
validate_no_duplicate_orders = gen.activity('Validate No Duplicate Orders')

subprocess_0 = gen.partial_order(dependencies=[(receive_order_confirmation,), (record_goods_receipt, vendor_creates_invoice)]) # Using parallel execution for goods receipt and invoice creation
subprocess_1 = gen.xor(None, remove_payment_block)
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt,), (clear_invoice,), (subprocess_1,)]) # Parallel execution within subprocess_4
subprocess_5 = gen.xor(None, subprocess_4)

final_model = gen.partial_order(dependencies = [(validate_no_duplicate_orders, create_purchase_order_item), # Added validation for duplicates 
(create_purchase_order_item, subprocess_0),
(subprocess_0, subprocess_5)])
