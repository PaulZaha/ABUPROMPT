from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional events
subprocess_0 = gen.xor(None, receive_order_confirmation)  # Receive Order Confirmation (optional)
subprocess_1 = gen.xor(None, vendor_creates_invoice)      # Vendor creates invoice (optional, informational)
subprocess_2 = gen.xor(None, remove_payment_block)        # Remove Payment Block (optional)

# Flattened, concurrency-first model with explicit gating only where necessary
final_model = gen.partial_order(dependencies=[
    # Start: after PO creation, run confirmation, logistics, and finance prep in parallel
    (create_purchase_order_item, subprocess_0),
    (create_purchase_order_item, subprocess_1),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, record_invoice_receipt),

    # Invoice flow: block removal (if any) only after invoice is recorded
    (record_invoice_receipt, subprocess_2),

    # Payment can clear only after both IR and GR are done, and any block is removed
    (record_invoice_receipt, clear_invoice),
    (record_goods_receipt, clear_invoice),
    (subprocess_2, clear_invoice)
])