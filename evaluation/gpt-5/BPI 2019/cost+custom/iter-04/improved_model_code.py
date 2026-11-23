from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# New controls to prevent duplicate orders
check_existing_po = gen.activity('Check for existing PO Item')
consolidate_duplicate = gen.activity('Consolidate with Existing PO Item')

# Optional, non-blocking confirmation
opt_order_confirmation = gen.xor(None, receive_order_confirmation)

# Optional external invoice creation; conditional clearing after invoice receipt
opt_vendor_invoice = gen.xor(None, vendor_creates_invoice)
blocked_clear = gen.partial_order(dependencies=[(remove_payment_block, clear_invoice)])
clear_invoice_direct = clear_invoice.copy()
post_invoice_decision = gen.xor(blocked_clear, clear_invoice_direct)

# Normal path: parallelize GR and IR; require both before clearing (three-way match)
normal_path = gen.partial_order(dependencies=[
    (create_purchase_order_item, opt_order_confirmation),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, opt_vendor_invoice),
    (create_purchase_order_item, record_invoice_receipt),
    (record_goods_receipt, post_invoice_decision),
    (record_invoice_receipt, post_invoice_decision)
])

# Branch: proceed normally or stop/merge if duplicate
decision = gen.xor(normal_path, consolidate_duplicate)

final_model = gen.partial_order(dependencies=[(check_existing_po, decision)])