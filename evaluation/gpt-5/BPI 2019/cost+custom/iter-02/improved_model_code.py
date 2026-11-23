from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Existing activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# New/added activities for improvements
check_existing_po_item = gen.activity('Check Existing PO Item')
link_to_existing_po_item = gen.activity('Link to Existing PO Item')
validate_po_item = gen.activity('Validate PO Item')
amend_po_item = gen.activity('Amend PO Item')
auto_receive_order_confirmation = gen.activity('Auto-Receive Order Confirmation')
three_way_match = gen.activity('3-way Match')
automatic_clear_invoice = gen.activity('Automatic Clear Invoice')
ers_settlement = gen.activity('Perform ERS Settlement')

# 1) Duplicate prevention gate: check first, then either link or create+validate
validation_loop = gen.loop(validate_po_item, amend_po_item)
create_and_validate = gen.partial_order(dependencies=[(create_purchase_order_item, validation_loop)])
create_or_link = gen.xor(link_to_existing_po_item, create_and_validate)
duplicate_gate = gen.partial_order(dependencies=[(check_existing_po_item, create_or_link)])

# 2) Order confirmation with automation option (optional overall)
order_confirmation = gen.xor(None, auto_receive_order_confirmation, receive_order_confirmation)

# 3) GR in parallel with optional vendor invoice creation
vendor_invoice_optional = gen.xor(None, vendor_creates_invoice)
gr_and_vendor_invoice = gen.partial_order(dependencies=[(record_goods_receipt,), (vendor_invoice_optional,)])

# 4) Invoice processing: ERS alternative or classic invoice path with 3-way match and exception handling
exception_path = gen.partial_order(dependencies=[(remove_payment_block, clear_invoice)])
post_match_branch = gen.xor(automatic_clear_invoice, exception_path)
match_stage = gen.partial_order(dependencies=[(record_invoice_receipt, three_way_match), (three_way_match, post_match_branch)])
invoice_or_ers = gen.xor(None, ers_settlement, match_stage)

# Final model sequencing
final_model = gen.partial_order(dependencies=[(duplicate_gate, order_confirmation), (order_confirmation, gr_and_vendor_invoice), (gr_and_vendor_invoice, invoice_or_ers)])