from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
acquire_creation_lock = gen.activity('Acquire Creation Lock')
check_duplicate_po = gen.activity('Check for Duplicate PO Item')
create_purchase_order_item = gen.activity('Create Purchase Order Item')
link_to_existing_po = gen.activity('Link to Existing Purchase Order Item')
release_creation_lock = gen.activity('Release Creation Lock')

receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
auto_clear_invoice = gen.activity('Auto Clear Invoice')
clear_invoice = gen.activity('Clear Invoice')

# Optional steps
receive_order_optional = gen.xor(None, receive_order_confirmation)
vendor_creates_invoice_optional = gen.xor(None, vendor_creates_invoice)

# Prevent duplicates: exclusive choice to create a new PO item or link to an existing one
create_or_link = gen.xor(create_purchase_order_item, link_to_existing_po)

# Manual clear path (used when automatic clearing is not possible)
manual_clear_path = gen.partial_order(dependencies=[(remove_payment_block, clear_invoice)])

# Exclusive clearing decision after both GR and invoice receipt are available
clearing_xor = gen.xor(auto_clear_invoice, manual_clear_path)

# Top-level process
final_model = gen.partial_order(
    dependencies=[
        (acquire_creation_lock, check_duplicate_po),
        (check_duplicate_po, create_or_link),
        (create_or_link, release_creation_lock),

        # After duplicate-safe PO is available, proceed in parallel
        (release_creation_lock, receive_order_optional),
        (release_creation_lock, record_goods_receipt),
        (release_creation_lock, record_invoice_receipt),
        (release_creation_lock, vendor_creates_invoice_optional),

        # Three-way match gating for clearing
        (record_goods_receipt, clearing_xor),
        (record_invoice_receipt, clearing_xor)
    ]
)