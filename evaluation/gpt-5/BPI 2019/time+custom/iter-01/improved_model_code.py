from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
check_existing_order = gen.activity('Check for Existing Order')
link_to_existing_order = gen.activity('Link to Existing Order')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional/choice constructs
rcv_conf_opt = gen.xor(None, receive_order_confirmation)
vend_inv_opt = gen.xor(None, vendor_creates_invoice)
rem_block_opt = gen.xor(None, remove_payment_block)
creation_choice = gen.xor(link_to_existing_order, create_purchase_order_item)

# Final model: maximize concurrency while ensuring correct gating for clearing and duplicates prevention
final_model = gen.partial_order(
    dependencies=[
        (check_existing_order, creation_choice),
        (creation_choice, rcv_conf_opt),
        (creation_choice, record_goods_receipt),
        (creation_choice, vend_inv_opt),
        (vend_inv_opt, record_invoice_receipt),
        (record_invoice_receipt, rem_block_opt),
        (record_invoice_receipt, clear_invoice),
        (record_goods_receipt, clear_invoice),
        (rem_block_opt, clear_invoice)
    ]
)