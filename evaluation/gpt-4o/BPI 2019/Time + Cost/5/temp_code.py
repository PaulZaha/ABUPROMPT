
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Subprocesses modified to increase concurrency
concurrent_subprocess = gen.partial_order(dependencies=[(receive_order_confirmation,), (vendor_creates_invoice,)])

# Refactored dependencies for better concurrency
subprocess_1 = gen.partial_order(dependencies=[(record_goods_receipt,), (concurrent_subprocess,)])
subprocess_2 = gen.partial_order(dependencies=[(record_invoice_receipt, remove_payment_block), (remove_payment_block, clear_invoice)])

# Removed unnecessary XOR optional subprocess to streamline process execution
final_model = gen.partial_order(dependencies=[(create_purchase_order_item, subprocess_1), (subprocess_1, subprocess_2)])
