from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps modeled explicitly
oc_opt = gen.xor(None, receive_order_confirmation)
vendor_invoice_opt = gen.xor(None, vendor_creates_invoice)
remove_block_opt = gen.xor(None, remove_payment_block)

# Maximize concurrency after PO creation; ensure payment is only cleared after
# both invoice processing and goods receipt are completed.
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, oc_opt),
    (create_purchase_order_item, vendor_invoice_opt),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, record_invoice_receipt),
    (record_invoice_receipt, remove_block_opt),
    (remove_block_opt, clear_invoice),
    (record_goods_receipt, clear_invoice)
])