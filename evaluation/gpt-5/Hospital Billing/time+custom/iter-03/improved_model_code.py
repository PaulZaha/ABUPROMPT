from generator.model_generator import ModelGenerator

gen = ModelGenerator()

new = gen.activity('NEW')
delete = gen.activity('DELETE')
change_diagn = gen.activity('CHANGE DIAGN')
fin = gen.activity('FIN')
release = gen.activity('RELEASE')
code_ok = gen.activity('CODE OK')
billed = gen.activity('BILLED')

# Allow 0..n diagnosis changes before the quality gate
change_loop = gen.loop(None, change_diagn)

# Main processing path with safe concurrency and enforced quality gates
process_path = gen.partial_order(
    dependencies=[
        (release,),
        (change_loop,),
        (code_ok,),
        (billed,),
        (fin,),
        (release, code_ok),
        (change_loop, code_ok),
        (code_ok, billed),
        (billed, fin)
    ]
)

# After NEW, choose either DELETE or execute the main process
final_model = gen.partial_order(dependencies=[(new, gen.xor(delete, process_path))])