
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')  # Now compulsory
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

subprocess_3 = gen.partial_order(dependencies = [(record_goods_receipt,), (vendor_creates_invoice,)])
subprocess_4 = gen.partial_order(dependencies = [(record_invoice_receipt,), (remove_payment_block, clear_invoice)])  # Re-modelled where dependencies are explicit.
subprocess_5 = gen.xor(None, subprocess_4)  # Retained optional execution of subprocess_4

final_model = gen.partial_order(dependencies = [(create_purchase_order_item, subprocess_3), (subprocess_3, subprocess_5)])  # Removed subprocess_0
