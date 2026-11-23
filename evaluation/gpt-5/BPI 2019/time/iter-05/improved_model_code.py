from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps
opt_receive_order_confirmation = gen.xor(None, receive_order_confirmation)
opt_remove_payment_block = gen.xor(None, remove_payment_block)

# Invoice processing subflow: starts after PO creation and runs independently of GR
invoice_flow = gen.partial_order(dependencies=[
    (vendor_creates_invoice, record_invoice_receipt),
    (record_invoice_receipt, opt_remove_payment_block),
    (opt_remove_payment_block, clear_invoice),
    (record_invoice_receipt, clear_invoice)
])

# Entire invoice flow can be skipped when no invoice exists
opt_invoice_flow = gen.xor(None, invoice_flow)

# Final model: three concurrent branches after PO creation
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, opt_receive_order_confirmation),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, opt_invoice_flow)
])