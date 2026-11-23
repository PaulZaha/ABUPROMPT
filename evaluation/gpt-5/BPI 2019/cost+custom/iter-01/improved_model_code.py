from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
check_existing_po_item = gen.activity('Check for Existing PO Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
auto_3_way_match = gen.activity('Auto 3-Way Match')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps
opt_receive_order_confirmation = gen.xor(None, receive_order_confirmation)
opt_vendor_creates_invoice = gen.xor(None, vendor_creates_invoice)
opt_manual_block = gen.xor(None, remove_payment_block)

# Concurrency of goods receipt and vendor invoice signal
gr_and_vendor = gen.partial_order(dependencies=[(record_goods_receipt,), (opt_vendor_creates_invoice,)])

# Invoice processing with automated 3-way match and exception-only manual block removal
invoice_processing = gen.partial_order(dependencies=[
    (record_invoice_receipt, auto_3_way_match),
    (auto_3_way_match, opt_manual_block),
    (opt_manual_block, clear_invoice)
])
opt_invoice_processing = gen.xor(None, invoice_processing)

# Core PO execution path (only if not a duplicate)
po_execution = gen.partial_order(dependencies=[
    (create_purchase_order_item, opt_receive_order_confirmation),
    (opt_receive_order_confirmation, gr_and_vendor),
    (gr_and_vendor, opt_invoice_processing)
])

# Duplicate-prevention gate: proceed with PO execution only if not a duplicate
proceed_after_dedup = gen.xor(None, po_execution)

final_model = gen.partial_order(dependencies=[
    (check_existing_po_item, proceed_after_dedup)
])