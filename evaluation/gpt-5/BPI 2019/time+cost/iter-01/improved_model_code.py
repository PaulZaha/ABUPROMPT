from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps modeled via xor(None, ...)
subprocess_0 = gen.xor(None, receive_order_confirmation)  # Receive Order Confirmation is optional
subprocess_1 = gen.xor(None, vendor_creates_invoice)      # Vendor creates invoice is optional
subprocess_2 = gen.xor(None, remove_payment_block)        # Remove Payment Block is optional

# Improved process: more concurrency and stricter gating for payment
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, subprocess_0),         # Confirmation can happen after PO creation, but doesn't gate others
    (create_purchase_order_item, record_goods_receipt), # Goods receipt can proceed after PO creation
    (create_purchase_order_item, subprocess_1),         # Vendor may create invoice after PO creation
    (subprocess_1, record_invoice_receipt),             # Record invoice only after vendor creates invoice
    (record_invoice_receipt, subprocess_2),             # If a block exists, remove it after invoice is recorded
    (record_invoice_receipt, clear_invoice),            # Clear invoice only after invoice is recorded
    (record_goods_receipt, clear_invoice)               # And only after goods receipt is recorded (3-way match)
])