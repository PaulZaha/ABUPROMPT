
from generator.model_generator import ModelGenerator 

gen = ModelGenerator()

a_create_application = gen.activity('A_Create Application')
a_submitted = gen.activity('A_Submitted')
w_handle_leads = gen.activity('W_Handle leads')
w_complete_application = gen.activity('W_Complete application')
a_concept = gen.activity('A_Concept')
a_accepted = gen.activity('A_Accepted')
o_create_offer = gen.activity('O_Create Offer')
o_created = gen.activity('O_Created')
o_sent_mail_and_online = gen.activity('O_Sent (mail and online)')
w_call_after_offers = gen.activity('W_Call after offers')
a_complete = gen.activity('A_Complete')
a_cancelled = gen.activity('A_Cancelled')
o_cancelled = gen.activity('O_Cancelled')

# Streamline subprocess to handle leads and complete application into one
streamlined_subprocess_0_1 = gen.partial_order(dependencies=[(w_handle_leads, w_complete_application)])
# Optimize optional subprocess handling concepts
optimized_subprocess_2_7 = gen.xor(a_concept, gen.partial_order(dependencies = [(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)]))

# Optimize cancellation and completion subprocesses
optimized_subprocess_5_8 = gen.xor(a_complete, a_cancelled)

# Generate final model optimizing dependencies and loops
final_model = gen.partial_order(dependencies = [
    (a_create_application, a_submitted), 
    (a_submitted, streamlined_subprocess_0_1),
    (streamlined_subprocess_0_1, optimized_subprocess_2_7),
    (optimized_subprocess_2_7, w_call_after_offers),
    (w_call_after_offers, optimized_subprocess_5_8),
    (optimized_subprocess_5_8, o_cancelled)
])
