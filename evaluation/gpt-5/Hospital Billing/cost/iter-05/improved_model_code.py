from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Optional diagnosis change only when billing proceeds
opt_change_diagn = gen.xor(None, change_diagn)

# Mandatory, ordered billing steps when billing path is chosen
billing_flow = gen.partial_order(dependencies=[
    (opt_change_diagn, release),
    (release, code_ok),
    (code_ok, billed)
])

# Decide to bill or skip all billing work after FIN
bill_or_skip = gen.xor(None, billing_flow)

# Ensure FIN precedes any billing work to avoid rework
processing = gen.partial_order(dependencies=[(fin, bill_or_skip)])

# After NEW, either delete immediately or process; removed pure skip to avoid idle WIP
post_new = gen.xor(delete, processing)

final_model = gen.partial_order(dependencies=[(new, post_new)])