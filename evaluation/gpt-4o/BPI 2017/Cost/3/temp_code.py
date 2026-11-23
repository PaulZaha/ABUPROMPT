
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

# Optimization begins here

# Remove unnecessary loops for handle leads and complete application subprocess
subprocess_0 = w_handle_leads 
subprocess_1 = w_complete_application 

# Simplify concept phase
subprocess_2 = gen.xor(None, a_concept)
subprocess_3 =  gen.partial_order(dependencies=[(a_accepted, o_create_offer), (o_create_offer, o_created), (o_created, o_sent_mail_and_online)])
subprocess_3 = gen.xor(subprocess_3, None)  # make offer creation optional if not beneficial

# Optimize offer follow-up
subprocess_4 = gen.xor(w_call_after_offers, None)

# Simplify cancel procedure
subprocess_5 = gen.xor(a_cancelled, o_cancelled)

# Submission and handling
subprocess_6 = gen.partial_order(dependencies = [(a_submitted, subprocess_0)])

# Simplify acceptance and concept subprocess
subprocess_7 = subprocess_3 

# Optimize complete and cancel branching
subprocess_8 = gen.xor(a_complete, subprocess_5)

# Reduce redundancy in initial submission process 
subprocess_9 = subprocess_6

subprocess_10 = gen.partial_order(dependencies = [(subprocess_2, subprocess_7)])

# Reduce iterative offer contacts
subprocess_11 = gen.xor(subprocess_4, subprocess_8)

# Reducing iterative applications
subprocess_12 = gen.partial_order(dependencies=[subprocess_1, subprocess_10])

final_model = gen.partial_order(dependencies = [(a_create_application, subprocess_9), (subprocess_9, subprocess_12), (subprocess_12, subprocess_11)]) 
