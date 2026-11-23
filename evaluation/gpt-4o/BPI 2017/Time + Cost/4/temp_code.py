
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

loop_optimized_leads = gen.loop(w_handle_leads, None)  # Assume improvement in process to qualify leads faster
loop_optimized_application = gen.loop(w_complete_application, None)  # Optimized complete application loop
subprocess_concept_optimized = gen.xor(a_concept, None)  # Streamlined decision making for concepts
subprocess_offer_creation = gen.partial_order(dependencies = [(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])
subprocess_automated_callback = gen.loop(w_call_after_offers, None)  # Automated follow-up, consider streamlining or automating callbacks
subprocess_cancel_offer = gen.partial_order(dependencies = [(a_cancelled, o_cancelled)])
subprocess_application = gen.partial_order(dependencies = [(a_submitted, loop_optimized_leads)])
subprocess_offer_decision = gen.xor(subprocess_offer_creation, None)  # Consolidated optional offer creation decision
subprocess_complete_cancel = gen.xor(subprocess_cancel_offer, a_complete)
subprocess_submission_optimized = gen.xor(None, subprocess_application)
subprocess_concept_offer_decision = gen.partial_order(dependencies = [(subprocess_concept_optimized, subprocess_offer_decision)])
subprocess_offer_call_loop = gen.loop(subprocess_automated_callback, subprocess_complete_cancel)
subprocess_application_complete_concept = gen.loop(loop_optimized_application, subprocess_concept_offer_decision)

final_model = gen.partial_order(dependencies = [(a_create_application, subprocess_submission_optimized), (subprocess_submission_optimized, subprocess_application_complete_concept), (subprocess_application_complete_concept, subprocess_offer_call_loop)])   
