from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
auto_record_invoice_receipt = gen.activity('Auto-Record Invoice Receipt (EDI)')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')
automatic_clear_invoice = gen.activity('Automatic Clear Invoice')

# Optional confirmation and vendor invoice (external)
opt_order_confirmation = gen.xor(None, receive_order_confirmation)
opt_vendor_invoice = gen.xor(None, vendor_creates_invoice)

# Invoice receipt: prefer EDI automation, fall back to manual
invoice_receipt_choice = gen.xor(auto_record_invoice_receipt, record_invoice_receipt)

# Manual exception resolution: optional block removal then manual clearing
opt_remove_block = gen.xor(None, remove_payment_block)
manual_resolution = gen.partial_order(dependencies=[(opt_remove_block, clear_invoice)])

# Clearing: automatic STP vs manual exception path
clear_choice = gen.xor(automatic_clear_invoice, manual_resolution)

# Invoice processing chain (receipt then resolution)
invoice_chain = gen.partial_order(dependencies=[(invoice_receipt_choice, clear_choice)])

# Entire invoice processing can be skipped (e.g., free-of-charge orders)
opt_invoice_process = gen.xor(None, invoice_chain)

# Final process: parallelize confirmation; gate invoice processing on GR and invoice availability
final_model = gen.partial_order(
    dependencies=[
        (create_purchase_order_item, opt_order_confirmation),
        (create_purchase_order_item, record_goods_receipt),
        (create_purchase_order_item, opt_vendor_invoice),
        (record_goods_receipt, opt_invoice_process),
        (opt_vendor_invoice, opt_invoice_process),
    ]
)