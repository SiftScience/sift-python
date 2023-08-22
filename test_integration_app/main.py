from events_api import test_events_api
from decisions_api import test_decisions_api
from workflows_api import test_workflows_api
from score_api import test_score_api
from verifications_api import test_verification_api
from labels_api import test_labels_api
from psp_merchant_api import test_psp_merchant_api

#Events APIs

# test_events_api.add_item_to_cart()

# test_events_api.add_promotion()

# test_events_api.chargeback()

# test_events_api.content_status()

# test_events_api.create_account()

# test_events_api.create_content_comment()

# test_events_api.create_content_listing()

# test_events_api.create_content_message()

# test_events_api.create_content_post()

# test_events_api.create_content_profile()

# test_events_api.create_content_review()

# test_events_api.create_order()

# test_events_api.flag_content()

# test_events_api.link_session_to_user()

# test_events_api.login()

# test_events_api.logout()

# test_events_api.order_status()

# test_events_api.remove_item_from_cart()

# test_events_api.security_notification()

# test_events_api.transaction()

# test_events_api.update_account()

# test_events_api.update_content_comment()

# test_events_api.update_content_listing()

# test_events_api.update_content_message()

# test_events_api.update_content_post()

# test_events_api.update_content_profile()

# test_events_api.update_content_review()

# test_events_api.update_order()

# test_events_api.update_password()

# test_events_api.verification()

# Decision APIs

# test_decisions_api.apply_user_decision_request()

# test_decisions_api.apply_order_decision_request()

# test_decisions_api.apply_session_decision()

# test_decisions_api.apply_content_decision()

# test_decisions_api.get_user_decisions()

# test_decisions_api.get_order_decisions()

# test_decisions_api.get_content_decisions()

# test_decisions_api.get_session_decisions()

# test_decisions_api.get_decisions("session") #user, order, content, session

# Workflows APIs

# test_workflows_api.get_workflow_status("workflow_run_id")

# Score APIs

# test_score_api.create_order_with_return_score()

# test_score_api.get_score()

# test_score_api.get_user_score()

# test_score_api.rescore_user()

# Labeling

# test_labels_api.user_label()

# test_labels_api.user_unlabel()

# Verification APIs

# test_verification_api.send()

# test_verification_api.resend()

# test_verification_api.check("271571")

# PSP Merchant APIs

# test_psp_merchant_api.create_merchant()

# test_psp_merchant_api.edit_merchant()

# test_psp_merchant_api.get_a_merchant_profile()

# test_psp_merchant_api.get_merchant_profiles()

test_psp_merchant_api.get_merchant_profiles(batch_size=2, batch_token="64d0a6a5afb931525995e75b")