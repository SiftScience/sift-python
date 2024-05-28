import string
import random

from events_api import test_events_api
from decisions_api import test_decisions_api
from workflows_api import test_workflows_api
from score_api import test_score_api
from verifications_api import test_verification_api
from psp_merchant_api import test_psp_merchant_api

class Utils:
    def isOK(self, response):
        if(hasattr(response, 'status')):
            return ((response.status == 0) and ((response.http_status_code == 200) or (response.http_status_code == 201)))
        else:
            return ((response.http_status_code == 200) or (response.http_status_code == 201))

    def is_ok_with_warnings(self, response):
        return self.isOK(response) and \
            hasattr(response, 'body') and \
            len(response.body['warnings']) > 0

    def is_ok_without_warnings(self, response):
        return self.isOK(response) and \
            hasattr(response, 'body') and \
            'warnings' not in response.body

def runAllMethods():
    objUtils = Utils()
    objEvents = test_events_api.EventsAPI()
    objDecision = test_decisions_api.DecisionAPI()
    objScore = test_score_api.ScoreAPI()
    objWorkflow = test_workflows_api.WorkflowsAPI()
    objVerification = test_verification_api.VerificationAPI()
    objPSPMerchant = test_psp_merchant_api.PSPMerchantAPI()

    # Events APIs
    assert (objUtils.isOK(objEvents.add_item_to_cart()) == True)
    assert (objUtils.isOK(objEvents.add_promotion()) == True)
    assert (objUtils.isOK(objEvents.chargeback()) == True)
    assert (objUtils.isOK(objEvents.content_status()) == True)
    assert (objUtils.isOK(objEvents.create_account()) == True)
    assert (objUtils.isOK(objEvents.create_content_comment()) == True)
    assert (objUtils.isOK(objEvents.create_content_listing()) == True)
    assert (objUtils.isOK(objEvents.create_content_message()) == True)
    assert (objUtils.isOK(objEvents.create_content_post()) == True)
    assert (objUtils.isOK(objEvents.create_content_profile()) == True)
    assert (objUtils.isOK(objEvents.create_content_review()) == True)
    assert (objUtils.isOK(objEvents.create_order()) == True)
    assert (objUtils.isOK(objEvents.flag_content()) == True)
    assert (objUtils.isOK(objEvents.link_session_to_user()) == True)
    assert (objUtils.isOK(objEvents.login()) == True)
    assert (objUtils.isOK(objEvents.logout()) == True)
    assert (objUtils.isOK(objEvents.order_status()) == True)
    assert (objUtils.isOK(objEvents.remove_item_from_cart()) == True)
    assert (objUtils.isOK(objEvents.security_notification()) == True)
    assert (objUtils.isOK(objEvents.transaction()) == True)
    assert (objUtils.isOK(objEvents.update_account()) == True)
    assert (objUtils.isOK(objEvents.update_content_comment()) == True)
    assert (objUtils.isOK(objEvents.update_content_listing()) == True)
    assert (objUtils.isOK(objEvents.update_content_message()) == True)
    assert (objUtils.isOK(objEvents.update_content_post()) == True)
    assert (objUtils.isOK(objEvents.update_content_profile()) == True)
    assert (objUtils.isOK(objEvents.update_content_review()) == True)
    assert (objUtils.isOK(objEvents.update_order()) == True)
    assert (objUtils.isOK(objEvents.update_password()) == True)
    assert (objUtils.isOK(objEvents.verification()) == True)

    # Testing include warnings query param
    assert (objUtils.is_ok_without_warnings(objEvents.create_order()) == True)
    assert (objUtils.is_ok_with_warnings(objEvents.create_order_with_warnings()) == True)

    print("Events API Tested")

    # Decision APIs
    assert (objUtils.isOK(objDecision.apply_user_decision()) == True)
    assert (objUtils.isOK(objDecision.apply_order_decision()) == True)
    assert (objUtils.isOK(objDecision.apply_session_decision()) == True)
    assert (objUtils.isOK(objDecision.apply_content_decision()) == True)
    assert (objUtils.isOK(objDecision.get_user_decisions()) == True)
    assert (objUtils.isOK(objDecision.get_order_decisions()) == True)
    assert (objUtils.isOK(objDecision.get_content_decisions()) == True)
    assert (objUtils.isOK(objDecision.get_session_decisions()) == True)
    assert (objUtils.isOK(objDecision.get_decisions()) == True)
    print("Decision API Tested")

    # Workflows APIs
    assert (objUtils.isOK(objWorkflow.synchronous_workflows()) == True)
    print("Workflow API Tested")

    # Score APIs
    assert (objUtils.isOK(objScore.get_user_score()) == True)
    print("Score API Tested")

    # Verification APIs
    assert (objUtils.isOK(objVerification.send()) == True)
    assert (objUtils.isOK(objVerification.resend()) == True)
    checkResponse = objVerification.check()
    assert (objUtils.isOK(checkResponse) == True)
    assert (checkResponse.body["status"] == 50)
    print("Verification API Tested")

    # PSP Merchant APIs
    merchant_id = 'merchant_id_test_app' + ''.join(random.choices(string.digits, k = 7))
    assert (objUtils.isOK(objPSPMerchant.create_merchant(merchant_id)) == True)
    assert (objUtils.isOK(objPSPMerchant.edit_merchant(merchant_id)) == True)
    assert (objUtils.isOK(objPSPMerchant.get_merchant_profiles()) == True)
    assert (objUtils.isOK(objPSPMerchant.get_merchant_profiles(batch_size=10, batch_token=None)) == True)
    print("PSP Merchant API Tested")

    print("API Integration tests execution finished")

runAllMethods()
