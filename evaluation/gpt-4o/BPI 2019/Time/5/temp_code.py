
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Remove optionality from receiving order confirmation
subprocess_0 = receive_order_confirmation

# Allow concurrency for goods receipt and vendor invoice creation
subprocess_1 = gen.partial_order(dependencies = [(record_goods_receipt,), (vendor_creates_invoice,)])
# Remove optionality from removing payment block
subprocess_2 = gen.partial_order(dependencies = [(record_invoice_receipt,), (remove_payment_block, clear_invoice)])

# Redefine the final model - ensuring clear sequential dependency
final_model = gen.partial_order(dependencies = [(create_purchase_order_item, subprocess_0), (subprocess_0, subprocess_1), (subprocess_1, subprocess_2)]) 
