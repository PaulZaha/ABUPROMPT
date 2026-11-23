from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
record_goods_receipt = gen.activity('Record Goods Receipt')
auto_record_e_invoice = gen.activity('Auto-Record e-Invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')
auto_clear_invoice = gen.activity('Auto-Clear Invoice')

# Invoice receipt can be auto or manual (promotes straight-through processing)
invoice_receipt_subprocess = gen.xor(auto_record_e_invoice, record_invoice_receipt)

# Clearing: auto-clear on 3-way match, or manual exception path
clearing_exception_path = gen.partial_order(dependencies=[(remove_payment_block, clear_invoice)])
clearing_xor = gen.xor(auto_clear_invoice, clearing_exception_path)

# Final model: GR and Invoice Receipt in parallel; clearing only after both are done
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, record_goods_receipt),
    (create_purchase_order_item, invoice_receipt_subprocess),
    (record_goods_receipt, clearing_xor),
    (invoice_receipt_subprocess, clearing_xor)
])