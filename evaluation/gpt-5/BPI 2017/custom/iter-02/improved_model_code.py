from generator.model_generator import ModelGenerator

gen = ModelGenerator()

# Original activities
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

# New customer information activities
c_confirm_application_created = gen.activity('C_Confirm Application Created')
c_notify_submission_received = gen.activity('C_Notify Submission Received')
c_status_update_leads = gen.activity('C_Notify Status: Lead Handling')
c_notify_under_review = gen.activity('C_Notify Under Review')
c_notify_accepted = gen.activity('C_Notify Accepted')
c_notify_offer_created = gen.activity('C_Notify Offer Created')
c_notify_offer_sent = gen.activity('C_Notify Offer Sent')
c_notify_call_outcome = gen.activity('C_Notify Call Outcome')
c_notify_completion = gen.activity('C_Notify Completion')
c_notify_cancellation = gen.activity('C_Notify Cancellation')
c_status_update_completion = gen.activity('C_Notify Status: Application Processing')
c_request_additional_info = gen.activity('C_Request Additional Information')

# Enhanced subprocesses with embedded customer notifications
subprocess_0 = gen.loop(gen.partial_order(dependencies=[(w_handle_leads, c_status_update_leads)]), None)

subprocess_1 = gen.loop(
    gen.partial_order(
        dependencies=[
            (w_complete_application, c_status_update_completion),
            (w_complete_application, gen.xor(None, c_request_additional_info))
        ]
    ),
    None
)

subprocess_2 = gen.xor(None, gen.partial_order(dependencies=[(a_concept, c_notify_under_review)]))

subprocess_3 = gen.partial_order(
    dependencies=[
        (a_accepted, c_notify_accepted),
        (c_notify_accepted, o_create_offer),
        (o_create_offer, o_created),
        (o_created, c_notify_offer_created),
        (c_notify_offer_created, o_sent_mail_and_online),
        (o_sent_mail_and_online, c_notify_offer_sent)
    ]
)

subprocess_4 = gen.loop(gen.partial_order(dependencies=[(w_call_after_offers, c_notify_call_outcome)]), None)

subprocess_5 = gen.partial_order(dependencies=[(a_cancelled, c_notify_cancellation), (c_notify_cancellation, o_cancelled)])

subprocess_6 = gen.partial_order(dependencies=[(a_submitted, c_notify_submission_received), (c_notify_submission_received, subprocess_0)])

subprocess_7 = gen.xor(None, subprocess_3)

subprocess_8 = gen.xor(gen.partial_order(dependencies=[(a_complete, c_notify_completion)]), subprocess_5)

subprocess_9 = gen.xor(None, subprocess_6)

subprocess_10 = gen.partial_order(dependencies=[(subprocess_2, subprocess_7)])

subprocess_11 = gen.loop(subprocess_4, subprocess_8)

subprocess_12 = gen.loop(subprocess_1, subprocess_10)

final_model = gen.partial_order(
    dependencies=[
        (a_create_application, c_confirm_application_created),
        (c_confirm_application_created, subprocess_9),
        (subprocess_9, subprocess_12),
        (subprocess_12, subprocess_11)
    ]
)