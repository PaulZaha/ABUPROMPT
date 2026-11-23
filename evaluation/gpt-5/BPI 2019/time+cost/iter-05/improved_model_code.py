from generator.model_generator import ModelGenerator

gen = ModelGenerator()

create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
automated_three_way_match = gen.activity('Automated 3-Way Match')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

optional_order_confirmation = gen.xor(None, receive_order_confirmation)
optional_remove_payment_block = gen.xor(None, remove_payment_block)

final_model = gen.partial_order(dependencies = [
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, record_invoice_receipt),
    (create_purchase_order_item, optional_order_confirmation),
    (record_goods_receipt, automated_three_way_match),
    (record_invoice_receipt, automated_three_way_match),
    (automated_three_way_match, optional_remove_payment_block),
    (optional_remove_payment_block, clear_invoice)
])