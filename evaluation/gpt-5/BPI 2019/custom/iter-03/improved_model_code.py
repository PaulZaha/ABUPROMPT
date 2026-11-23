from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Original activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# New activities to prevent duplicates
check_duplicate_order = gen.activity('Check for Duplicate Order')
approve_order_creation = gen.activity('Approve Order Creation')
link_to_existing_order = gen.activity('Link to Existing Order')

# Existing subprocesses
subprocess_0 = gen.xor(None, receive_order_confirmation)
subprocess_1 = gen.xor(None, vendor_creates_invoice)
subprocess_2 = gen.xor(None, remove_payment_block)
subprocess_3 = gen.partial_order(dependencies=[(record_goods_receipt,), (subprocess_1,)])
subprocess_4 = gen.partial_order(dependencies=[(record_invoice_receipt, subprocess_2), (subprocess_2, clear_invoice)])
subprocess_5 = gen.xor(None, subprocess_4)

# Create branch: requires approval before creation, then proceeds with the original flow
create_branch = gen.partial_order(
    dependencies=[
        (approve_order_creation, create_purchase_order_item),
        (create_purchase_order_item, subprocess_0),
        (subprocess_0, subprocess_3),
        (subprocess_3, subprocess_5)
    ]
)

# Decision point: proceed to create branch or link to an existing order if duplicate detected
decision_xor = gen.xor(create_branch, link_to_existing_order)

# Final model: always check for duplicates first, then make an exclusive choice
final_model = gen.partial_order(dependencies=[(check_duplicate_order, decision_xor)])