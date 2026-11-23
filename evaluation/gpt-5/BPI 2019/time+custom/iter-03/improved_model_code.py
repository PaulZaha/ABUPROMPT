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

# Duplicate prevention and fast-path handling
run_duplicate_check = gen.activity('Run Duplicate Check')
update_existing_po_item = gen.activity('Update Existing PO Item')

# Matching and exception handling
perform_three_way_match = gen.activity('Perform 3-Way Match')
resolve_invoice_discrepancy = gen.activity('Resolve Invoice Discrepancy')

# Optional steps as exclusive choices
optional_order_confirmation = gen.xor(None, receive_order_confirmation)
optional_vendor_invoice = gen.xor(None, vendor_creates_invoice)

# Exception path when 3-way match fails
mismatch_path = gen.partial_order(dependencies=[
    (resolve_invoice_discrepancy, remove_payment_block),
    (remove_payment_block, clear_invoice)
])

# Decision after matching: auto-clear vs. exception handling
clear_invoice_fast = clear_invoice.copy()
post_match_decision = gen.xor(clear_invoice_fast, mismatch_path)

# Non-duplicate processing with increased concurrency and early matching
non_duplicate_flow = gen.partial_order(dependencies=[
    (create_purchase_order_item, optional_order_confirmation),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, optional_vendor_invoice),
    (optional_vendor_invoice, record_invoice_receipt),
    (record_goods_receipt, perform_three_way_match),
    (record_invoice_receipt, perform_three_way_match),
    (perform_three_way_match, post_match_decision)
])

# Duplicate-prevention gate: either proceed with normal flow or update existing order (no new PO)
duplicate_gate = gen.xor(non_duplicate_flow, update_existing_po_item)

final_model = gen.partial_order(dependencies=[
    (run_duplicate_check, duplicate_gate)
])