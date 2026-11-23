from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
check_duplicate_po_item = gen.activity('Check Duplicate PO Item')
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
perform_3_way_match = gen.activity('Perform 3-Way Match')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps
receive_confirmation_optional = gen.xor(None, receive_order_confirmation)
remove_payment_block_optional = gen.xor(None, remove_payment_block)
vendor_invoice_optional = gen.xor(None, vendor_creates_invoice)

# Invoice processing sequence (optional as a whole), guarded by 3-way match
invoice_flow = gen.partial_order(dependencies=[
    (record_invoice_receipt, perform_3_way_match),
    (perform_3_way_match, remove_payment_block_optional),
    (remove_payment_block_optional, clear_invoice)
])
invoice_flow_optional = gen.xor(None, invoice_flow)

# Core PO execution path (flattened dependencies, no nested partial_order under another)
po_full_path = gen.partial_order(dependencies=[
    (create_purchase_order_item, receive_confirmation_optional),
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, vendor_invoice_optional),
    # Invoice processing can start only after both GR and (optional) vendor invoice phase complete
    (vendor_invoice_optional, invoice_flow_optional),
    (record_goods_receipt, invoice_flow_optional)
])

# Gate: stop the whole process if a duplicate is detected
process_main_choice = gen.xor(po_full_path, None)

final_model = gen.partial_order(dependencies=[(check_duplicate_po_item, process_main_choice)])