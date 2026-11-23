from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
check_duplicate_order = gen.activity('Check for Duplicate Order')
cancel_duplicate_order = gen.activity('Cancel Duplicate Order')

receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Optional/conditional steps modeled via XOR(None, ...)
optional_receive_confirmation = gen.xor(None, receive_order_confirmation)
optional_vendor_invoice = gen.xor(None, vendor_creates_invoice)
optional_remove_payment_block = gen.xor(None, remove_payment_block)
optional_clear_invoice = gen.xor(None, clear_invoice)

# Continue branch after duplicate check: maximize parallelism and enforce matching for clearing
continue_subprocess = gen.partial_order(dependencies=[
    # Early invoice capture and optional block removal
    (record_invoice_receipt, optional_remove_payment_block),
    (optional_remove_payment_block, optional_clear_invoice),
    # Three-way match for clearing: wait for GR as well
    (record_goods_receipt, optional_clear_invoice),
    # Non-blocking, parallel informational steps
    (optional_receive_confirmation,),
    (optional_vendor_invoice,)
])

# Decision after duplicate check: either cancel (stop) or continue with the rest
decision = gen.xor(continue_subprocess, cancel_duplicate_order)

# Final model: enforce duplicate check gate before proceeding
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, check_duplicate_order),
    (check_duplicate_order, decision)
])