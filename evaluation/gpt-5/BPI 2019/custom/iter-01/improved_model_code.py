from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# New anti-duplicate controls
acquire_requisition_lock = gen.activity('Acquire Requisition Lock')
check_existing_order_item = gen.activity('Check for Existing Order Item')
reference_existing_order_item = gen.activity('Reference Existing Order Item')
release_requisition_lock = gen.activity('Release Requisition Lock')

# Existing optional and concurrent structures
subprocess_0 = gen.xor(None, receive_order_confirmation)
subprocess_1 = gen.xor(None, vendor_creates_invoice)
subprocess_2 = gen.xor(None, remove_payment_block)
subprocess_3 = gen.partial_order(dependencies=[(record_goods_receipt,), (subprocess_1,)])
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt, subprocess_2), (subprocess_2, clear_invoice)])
subprocess_5 = gen.xor(None, subprocess_4)

# Deduplication gate: either reference existing order item or create a new one
dedup_gate = gen.xor(reference_existing_order_item, create_purchase_order_item)

# Final model: lock -> check -> XOR (reference or create) -> release lock -> rest of the process
final_model = gen.partial_order(dependencies=[
    (acquire_requisition_lock, check_existing_order_item),
    (check_existing_order_item, dedup_gate),
    (dedup_gate, release_requisition_lock),
    (release_requisition_lock, subprocess_0),
    (subprocess_0, subprocess_3),
    (subprocess_3, subprocess_5)
])