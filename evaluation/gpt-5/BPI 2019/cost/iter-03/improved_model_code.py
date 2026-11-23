from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional order confirmation
after_po = gen.xor(None, receive_order_confirmation)

# Pre-settlement stage: ensure goods receipt before any settlement
pre_settlement = gen.partial_order(dependencies=[(record_goods_receipt,)])

# ERS branch (no invoice): directly clear based on GR
clear_invoice_ers = clear_invoice.copy()
ers_branch = clear_invoice_ers

# Invoice branch: vendor invoice -> record invoice -> optional unblock -> clear
payment_block_path = gen.xor(None, remove_payment_block)
invoice_branch = gen.partial_order(dependencies=[
    (vendor_creates_invoice, record_invoice_receipt),
    (record_invoice_receipt, payment_block_path),
    (payment_block_path, clear_invoice)
])

# Settlement choice after GR: ERS vs traditional invoicing vs skip (e.g., consignment)
settlement_alternatives = gen.xor(ers_branch, invoice_branch)
settlement_choice = gen.xor(None, settlement_alternatives)

final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, after_po),
    (after_po, pre_settlement),
    (pre_settlement, settlement_choice)
])