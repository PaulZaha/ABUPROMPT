
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Vendor creates invoice removed due to redundancy
# subprocess_0 now requires receiving confirmation as part of order processing
subprocess_0 = receive_order_confirmation

# subprocess_1 removed 
# subprocess_3 restructured to remove optional segment, focuses on goods receipt
subprocess_3 = gen.partial_order(dependencies = [(record_goods_receipt,)])

# subprocess_4 streamlined and focused on automating payment block removal
subprocess_4 = gen.partial_order(dependencies = [(record_invoice_receipt, clear_invoice)])

# subprocess_5 directly leads to invoice clearing, avoiding unnecessary XOR
# loop structure to automate retries, minimized manual reviews
subprocess_5 = gen.loop(subprocess_4, remove_payment_block)

final_model = gen.partial_order(dependencies = [
    (create_purchase_order_item, subprocess_0), 
    (subprocess_0, subprocess_3),
    (subprocess_3, subprocess_5)
])
