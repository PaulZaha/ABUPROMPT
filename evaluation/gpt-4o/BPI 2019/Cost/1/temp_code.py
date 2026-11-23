
from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

subprocess_0 = gen.partial_order(dependencies=[(record_goods_receipt,)])
subprocess_1 = gen.xor(vendor_creates_invoice, None)  # Making the creation optional if automated
subprocess_2_optimized = gen.partial_order(dependencies = [(record_invoice_receipt, clear_invoice)])
subprocess_2 = gen.xor(None, subprocess_2_optimized)

final_model = gen.partial_order(dependencies = [(create_purchase_order_item, subprocess_0), (subprocess_0, subprocess_1), (subprocess_1, subprocess_2)]) 
