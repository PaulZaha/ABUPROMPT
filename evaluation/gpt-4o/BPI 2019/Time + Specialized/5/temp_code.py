
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
verify_order_not_duplicate = gen.activity('Verify Order Not Duplicate')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Adding a verification step to check for duplicate orders
verify_and_create_order = gen.partial_order(dependencies = [(create_purchase_order_item, verify_order_not_duplicate), (verify_order_not_duplicate, receive_order_confirmation)])

# Making vendor creates invoice and remove payment block mandatory
invoice_subprocess = gen.partial_order(dependencies = [(record_invoice_receipt, vendor_creates_invoice),
                                                       (vendor_creates_invoice, remove_payment_block),
                                                       (remove_payment_block, clear_invoice)])

# Combining the goods receipt and invoice process into one mandatory process
goods_receipt_and_invoice_process = gen.partial_order(dependencies = [(record_goods_receipt, invoice_subprocess)])

final_model = gen.partial_order(dependencies = [(verify_and_create_order, goods_receipt_and_invoice_process)])
