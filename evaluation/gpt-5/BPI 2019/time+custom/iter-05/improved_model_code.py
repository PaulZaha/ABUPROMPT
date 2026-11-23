from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Added activities for duplicate prevention
check_duplicate_order = gen.activity('Check for Duplicate Order')
handle_duplicate_order = gen.activity('Handle Duplicate Order')

# Optional steps modeled via XOR
optional_order_confirmation = gen.xor(None, receive_order_confirmation)
optional_vendor_invoice = gen.xor(None, vendor_creates_invoice)
optional_remove_payment_block = gen.xor(None, remove_payment_block)

# Main (non-duplicate) flow: create PO, then parallel confirmation, GR, and invoice processing
proceed_flow = gen.partial_order(dependencies=[
    (create_purchase_order_item, optional_order_confirmation),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, optional_vendor_invoice),
    (optional_vendor_invoice, record_invoice_receipt),
    (record_invoice_receipt, optional_remove_payment_block),
    # Clear invoice only after both invoice path (through optional block) and goods receipt
    (record_goods_receipt, clear_invoice),
    (optional_remove_payment_block, clear_invoice)
])

# Decision: proceed with creation or handle duplicate and end
duplication_decision = gen.xor(proceed_flow, handle_duplicate_order)

# Final model: ensure duplicate check precedes the decision
final_model = gen.partial_order(dependencies=[(check_duplicate_order, duplication_decision)])