from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps
subprocess_0 = gen.xor(None, receive_order_confirmation)  # optional order confirmation
subprocess_1 = gen.xor(None, vendor_creates_invoice)      # optional vendor invoice creation (external)
subprocess_2 = gen.xor(None, remove_payment_block)        # optional payment block removal

# Invoice-processing chain kept inside an optional branch, but can now start right after PO creation
subprocess_4 = gen.partial_order(dependencies=[
    (record_invoice_receipt, subprocess_2),
    (subprocess_2, clear_invoice)
])
subprocess_5 = gen.xor(None, subprocess_4)  # optional invoice path: Record Invoice -> (optional) Remove Block -> Clear

# Final model: run independent branches in parallel immediately after PO creation
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, subprocess_0),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, subprocess_1),
    (create_purchase_order_item, subprocess_5)
])