from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
fin = gen.activity('FIN')
billed = gen.activity('BILLED')
invoice_sent = gen.activity('INVOICE SENT')

# Quality loop: enforce that any diagnosis change is followed by another CODE OK check
quality_loop = gen.loop(code_ok, change_diagn)

# Main processing sequence: RELEASE -> (CODE OK <-> CHANGE DIAGN loop) -> FIN -> BILLED -> INVOICE SENT
main_flow = gen.partial_order(dependencies=[
    (release, quality_loop),
    (quality_loop, fin),
    (fin, billed),
    (billed, invoice_sent)
])

# Explicit choice after NEW: either DELETE (invalid case) or run the full main flow
selection = gen.xor(delete, main_flow)

final_model = gen.partial_order(dependencies=[(new, selection)])