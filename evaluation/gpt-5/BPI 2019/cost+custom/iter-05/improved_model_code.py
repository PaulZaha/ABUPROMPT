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

# New activities for improvement
check_duplicate = gen.activity('Check for Duplicate Order')
consolidate_duplicate = gen.activity('Consolidate with Existing Order')

# Optional steps
confirm_opt = gen.xor(None, receive_order_confirmation)
vendor_invoice_opt = gen.xor(None, vendor_creates_invoice)
remove_block_opt = gen.xor(None, remove_payment_block)

# Invoice processing (optional as a group) with corrected dependencies
invoice_processing = gen.partial_order(dependencies=[
    (record_invoice_receipt, remove_block_opt),
    (remove_block_opt, clear_invoice),
    (record_invoice_receipt, clear_invoice)
])
invoice_processing_opt = gen.xor(None, invoice_processing)

# Normal processing path (executed only if not a duplicate)
proceed_flow = gen.partial_order(dependencies=[
    (create_purchase_order_item, confirm_opt),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, vendor_invoice_opt),
    (record_goods_receipt, invoice_processing_opt),
    (vendor_invoice_opt, invoice_processing_opt)
])

# Decision after duplicate check: consolidate (end) or proceed with new PO
decision = gen.xor(consolidate_duplicate, proceed_flow)

# Final model: always check duplicates first, then branch
final_model = gen.partial_order(dependencies=[
    (check_duplicate, decision)
])