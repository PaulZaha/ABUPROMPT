from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# New activities to prevent duplicate orders
place_creation_lock = gen.activity('Place Creation Lock')
check_for_duplicate = gen.activity('Check for Duplicate PO Item')
handle_duplicate = gen.activity('Handle Duplicate (Link/Abort)')
release_creation_lock = gen.activity('Release Creation Lock')

# Optional and concurrent subprocesses (original logic preserved)
subprocess_0 = gen.xor(None, receive_order_confirmation)  # optional order confirmation
subprocess_1 = gen.xor(None, vendor_creates_invoice)      # optional vendor invoice creation
subprocess_2 = gen.xor(None, remove_payment_block)        # optional payment block removal
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt, subprocess_2), (subprocess_2, clear_invoice)])
subprocess_5 = gen.xor(None, subprocess_4)                # optional invoice receipt -> (optional) remove block -> clear

# Creation path encapsulates the original downstream flow so it runs only when a new PO is created
# Flattened to avoid partial_order nested within another partial_order
creation_path = gen.partial_order(dependencies=[
    (create_purchase_order_item, subprocess_0),
    (subprocess_0, record_goods_receipt),
    (subprocess_0, subprocess_1),
    (record_goods_receipt, subprocess_5),
    (subprocess_1, subprocess_5)
])

# Decision: create new PO item or handle duplicate (link/abort)
duplicate_gate = gen.xor(handle_duplicate, creation_path)

# Final model: lock -> duplicate check -> decision -> release lock
final_model = gen.partial_order(dependencies=[
    (place_creation_lock, check_for_duplicate),
    (check_for_duplicate, duplicate_gate),
    (duplicate_gate, release_creation_lock)
])