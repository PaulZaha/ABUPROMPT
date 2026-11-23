
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Remove optional xor subprocesses for receive_order_confirmation
subprocess_0 = gen.partial_order(dependencies = [(receive_order_confirmation, create_purchase_order_item)])

# Execute vendor_creates_invoice and remove_payment_block concurrently
subprocess_1 = gen.partial_order(dependencies = [(vendor_creates_invoice,), (remove_payment_block,)])

# Record Invoice Receipt and Clear Invoice in sequence; simplified subprocess by removing optionality
subprocess_2 = gen.partial_order(dependencies = [(record_invoice_receipt, clear_invoice)])

# Consolidating subprocesses 3 and 5 to reduce decision points
final_model = gen.partial_order(dependencies = [(subprocess_0, record_goods_receipt), 
                                                (record_goods_receipt, subprocess_1), 
                                                (subprocess_1, subprocess_2)])
