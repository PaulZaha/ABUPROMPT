from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')
auto_match_and_clear_invoice = gen.activity('Auto-match and Clear Invoice')

# Optional steps
subprocess_0 = gen.xor(None, receive_order_confirmation)  # optional order confirmation
subprocess_1 = gen.xor(None, vendor_creates_invoice)      # optional vendor invoice event
subprocess_2 = gen.xor(None, remove_payment_block)        # optional payment block removal

# Manual invoice processing chain: Record invoice -> (optional) remove block -> clear
manual_invoice_processing = gen.partial_order(dependencies=[
    (record_invoice_receipt, subprocess_2),
    (subprocess_2, clear_invoice)
])

# Choose automated STP or manual processing
invoice_processing_choice = gen.xor(auto_match_and_clear_invoice, manual_invoice_processing)

# Entire invoice processing is optional (only executed if an invoice exists and matching is required)
invoice_processing_optional = gen.xor(None, invoice_processing_choice)

# Final orchestration: PO creation enables parallel confirmation, GR, and (optional) vendor invoice.
# Invoice processing (manual or STP) starts only after both GR and the vendor invoice event are available.
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, subprocess_1),
    (create_purchase_order_item, subprocess_0),
    (record_goods_receipt, invoice_processing_optional),
    (subprocess_1, invoice_processing_optional)
])