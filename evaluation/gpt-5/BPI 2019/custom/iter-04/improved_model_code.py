from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# New control activities to prevent duplicate orders
acquire_lock = gen.activity('Acquire PO Item Creation Lock')
duplicate_check = gen.activity('Check for Duplicate Purchase Order Item')
release_lock = gen.activity('Release PO Item Creation Lock')
reference_existing_order = gen.activity('Reference Existing Order')

# Existing process activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional and concurrent subprocesses (as in the original model)
subprocess_0 = gen.xor(None, receive_order_confirmation)
subprocess_1 = gen.xor(None, vendor_creates_invoice)
subprocess_2 = gen.xor(None, remove_payment_block)
subprocess_3 = gen.partial_order(dependencies=[(record_goods_receipt,), (subprocess_1,)])
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt, subprocess_2), (subprocess_2, clear_invoice)])
subprocess_5 = gen.xor(None, subprocess_4)

# Release lock is needed in both branches; create separate instances
release_lock_after_create = release_lock.copy()
release_lock_after_reference = release_lock.copy()

# Non-duplicate branch: create and then proceed with the original flow
not_duplicate_path = gen.partial_order(
    dependencies=[
        (create_purchase_order_item, release_lock_after_create),
        (release_lock_after_create, subprocess_0),
        (subprocess_0, subprocess_3),
        (subprocess_3, subprocess_5)
    ]
)

# Duplicate branch: do not create; reference existing order and release lock
duplicate_path = gen.partial_order(
    dependencies=[
        (reference_existing_order, release_lock_after_reference)
    ]
)

# Decision: proceed to create or reference existing order based on duplicate check
decision = gen.xor(not_duplicate_path, duplicate_path)

# Final model: short lock and duplicate check before branching
final_model = gen.partial_order(
    dependencies=[
        (acquire_lock, duplicate_check),
        (duplicate_check, decision)
    ]
)