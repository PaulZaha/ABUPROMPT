from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

optional_order_confirmation = gen.xor(None, receive_order_confirmation)
optional_vendor_invoice = gen.xor(None, vendor_creates_invoice)
optional_remove_block = gen.xor(None, remove_payment_block)

final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, optional_order_confirmation),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, optional_vendor_invoice),
    (optional_vendor_invoice, record_invoice_receipt),
    (record_invoice_receipt, optional_remove_block),
    (record_invoice_receipt, clear_invoice),
    (optional_remove_block, clear_invoice),
    (record_goods_receipt, clear_invoice)
])