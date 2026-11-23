
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Encouraging concurrency in subprocess_4
subprocess_1 = gen.xor(None, vendor_creates_invoice)
subprocess_2 = gen.xor(None, remove_payment_block)
subprocess_4 = gen.partial_order(dependencies = [
    (record_invoice_receipt,), 
    (subprocess_2, clear_invoice)
])

# Maintain subprocess_3 as partial order 
subprocess_3 = gen.partial_order(dependencies = [
    (record_goods_receipt,), 
    (subprocess_1,)
])

# Optimized high-level structure with reduced blocking paths
subprocess_0 = gen.xor(None, receive_order_confirmation)
subprocess_5 = gen.xor(None, subprocess_4)

# Adjust overall sequence for concurrency
final_model = gen.partial_order(dependencies = [
    (create_purchase_order_item, subprocess_0), 
    (subprocess_0, subprocess_3), 
    (subprocess_3, subprocess_5)
])
