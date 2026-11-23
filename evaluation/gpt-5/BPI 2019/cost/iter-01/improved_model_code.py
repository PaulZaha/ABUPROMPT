from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Core activities
create_purchase_order_item = gen.activity('Create Purchase Order Item')
receive_order_confirmation = gen.activity('Receive Order Confirmation')
record_goods_receipt = gen.activity('Record Goods Receipt')
vendor_creates_invoice = gen.activity('Vendor creates invoice')
record_invoice_receipt = gen.activity('Record Invoice Receipt')
remove_payment_block = gen.activity('Remove Payment Block')
clear_invoice = gen.activity('Clear Invoice')

# Automation activities to reduce manual effort/cost
auto_process_order_confirmation = gen.activity('Auto-Process Order Confirmation')
ers_settlement = gen.activity('ERS Settlement (Self-Billing)')
auto_post_clear_edi = gen.activity('Auto-Post and Clear EDI Invoice')

# Optional/automated order confirmation (skip or auto or manual)
rc_sub = gen.xor(None, auto_process_order_confirmation, receive_order_confirmation)

# Branch-specific copies to avoid cross-branch coupling of the same node
rgr_ers = record_goods_receipt.copy()
rgr_edi = record_goods_receipt.copy()
rgr_manual = record_goods_receipt.copy()

vci_edi = vendor_creates_invoice.copy()
vci_manual = vendor_creates_invoice.copy()

# Exception-only payment block
remove_payment_block_opt = gen.xor(None, remove_payment_block)

# ERS branch: self-billing after GR eliminates invoice receipt/clear
ers_path = gen.partial_order(dependencies=[
    (rgr_ers, ers_settlement)
])

# EDI STP branch: auto-post and clear after GR and vendor e-invoice
edi_stp_path = gen.partial_order(dependencies=[
    (rgr_edi, auto_post_clear_edi),
    (vci_edi, auto_post_clear_edi)
])

# Manual branch: manual invoice receipt, optional block removal, then clear after GR and invoice receipt
manual_path = gen.partial_order(dependencies=[
    (vci_manual, record_invoice_receipt),
    (record_invoice_receipt, remove_payment_block_opt),
    (record_invoice_receipt, clear_invoice),
    (remove_payment_block_opt, clear_invoice),
    (rgr_manual, clear_invoice)
])

# Settlement mode selection prioritizes automation (ERS/EDI) with manual as fallback
settlement_xor = gen.xor(ers_path, edi_stp_path, manual_path)

# Overall flow: create PO -> (skip/auto/manual) order confirmation -> settlement branch
final_model = gen.partial_order(dependencies=[
    (create_purchase_order_item, rc_sub),
    (rc_sub, settlement_xor)
])