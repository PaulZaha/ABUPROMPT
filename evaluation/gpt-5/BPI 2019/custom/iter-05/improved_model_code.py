from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
check_duplicate_po = gen.activity('Check for Duplicate PO')
log_duplicate = gen.activity('Log Duplicate and Notify Requester')
apply_po_lock = gen.activity('Apply PO Creation Lock')

# Downstream activities
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps
receive_conf_opt = gen.xor(None, receive_order_confirmation)
remove_block_opt = gen.xor(None, remove_payment_block)

# Invoice processing occurs only if vendor creates an invoice
invoice_chain = gen.partial_order(dependencies=[
    (vendor_creates_invoice, record_invoice_receipt),
    (record_invoice_receipt, remove_block_opt),
    (remove_block_opt, clear_invoice)
])
invoice_processing_opt = gen.xor(None, invoice_chain)

# No-duplicate path: create PO, lock it, then proceed with confirmation and parallel downstream processing
path_no_duplicate = gen.partial_order(dependencies=[
    (create_purchase_order_item, apply_po_lock),
    (apply_po_lock, receive_conf_opt),
    (receive_conf_opt, record_goods_receipt),
    (receive_conf_opt, invoice_processing_opt)
])

# Decision after duplicate check: either proceed or log-and-stop
decision_xor = gen.xor(path_no_duplicate, log_duplicate)

# Final model: mandatory duplicate check gates the entire process
final_model = gen.partial_order(dependencies=[
    (check_duplicate_po, decision_xor)
])