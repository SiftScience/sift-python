import random
import string

from decisions_api import test_decisions_api
from events_api import test_events_api
from psp_merchant_api import test_psp_merchant_api
from score_api import test_score_api
from verifications_api import test_verification_api
from workflows_api import test_workflows_api

from sift.client import Response


def is_ok(response: Response) -> bool:
    if hasattr(response, "status"):
        return response.status == 0 and response.http_status_code in (200, 201)

    return response.http_status_code in (200, 201)


def is_ok_with_warnings(response: Response) -> bool:
    return (
        is_ok(response)
        and hasattr(response, "body")
        and isinstance(response.body, dict)
        and bool(response.body["warnings"])
    )


def is_ok_without_warnings(response: Response) -> bool:
    return (
        is_ok(response)
        and hasattr(response, "body")
        and isinstance(response.body, dict)
        and "warnings" not in response.body
    )


def run_all_methods() -> None:
    obj_events = test_events_api.EventsAPI()
    obj_decisions = test_decisions_api.DecisionAPI()
    obj_score = test_score_api.ScoreAPI()
    obj_workflow = test_workflows_api.WorkflowsAPI()
    obj_verification = test_verification_api.VerificationAPI()
    obj_psp_merchant = test_psp_merchant_api.PSPMerchantAPI()

    # Events APIs
    assert is_ok(obj_events.add_item_to_cart())
    assert is_ok(obj_events.add_promotion())
    assert is_ok(obj_events.chargeback())
    assert is_ok(obj_events.content_status())
    assert is_ok(obj_events.create_account())
    assert is_ok(obj_events.create_content_comment())
    assert is_ok(obj_events.create_content_listing())
    assert is_ok(obj_events.create_content_message())
    assert is_ok(obj_events.create_content_post())
    assert is_ok(obj_events.create_content_profile())
    assert is_ok(obj_events.create_content_review())
    assert is_ok(obj_events.create_order())
    assert is_ok(obj_events.flag_content())
    assert is_ok(obj_events.link_session_to_user())
    assert is_ok(obj_events.login())
    assert is_ok(obj_events.logout())
    assert is_ok(obj_events.order_status())
    assert is_ok(obj_events.remove_item_from_cart())
    assert is_ok(obj_events.security_notification())
    assert is_ok(obj_events.transaction())
    assert is_ok(obj_events.update_account())
    assert is_ok(obj_events.update_content_comment())
    assert is_ok(obj_events.update_content_listing())
    assert is_ok(obj_events.update_content_message())
    assert is_ok(obj_events.update_content_post())
    assert is_ok(obj_events.update_content_profile())
    assert is_ok(obj_events.update_content_review())
    assert is_ok(obj_events.update_order())
    assert is_ok(obj_events.update_password())
    assert is_ok(obj_events.verification())

    # Testing include warnings query param
    assert is_ok_without_warnings(obj_events.create_order())
    assert is_ok_with_warnings(obj_events.create_order_with_warnings())

    print("Events API Tested")

    # Decision APIs
    assert is_ok(obj_decisions.apply_user_decision())
    assert is_ok(obj_decisions.apply_order_decision())
    assert is_ok(obj_decisions.apply_session_decision())
    assert is_ok(obj_decisions.apply_content_decision())
    assert is_ok(obj_decisions.get_user_decisions())
    assert is_ok(obj_decisions.get_order_decisions())
    assert is_ok(obj_decisions.get_content_decisions())
    assert is_ok(obj_decisions.get_session_decisions())
    assert is_ok(obj_decisions.get_decisions())
    print("Decision API Tested")

    # Workflows APIs
    assert is_ok(obj_workflow.synchronous_workflows())
    print("Workflow API Tested")

    # Score APIs
    assert is_ok(obj_score.get_user_score())
    print("Score API Tested")

    # Verification APIs
    assert is_ok(obj_verification.send())
    assert is_ok(obj_verification.resend())
    checkResponse = obj_verification.check()
    assert is_ok(checkResponse)
    assert isinstance(checkResponse.body, dict)
    assert checkResponse.body["status"] == 50
    print("Verification API Tested")

    # PSP Merchant APIs
    merchant_id = "merchant_id_test_app" + "".join(
        random.choices(string.digits, k=7)
    )
    assert is_ok(obj_psp_merchant.create_merchant(merchant_id))
    assert is_ok(obj_psp_merchant.edit_merchant(merchant_id))
    assert is_ok(obj_psp_merchant.get_merchant_profiles())
    assert is_ok(
        obj_psp_merchant.get_merchant_profiles(batch_size=10, batch_token=None)
    )
    print("PSP Merchant API Tested")

    print("API Integration tests execution finished")


run_all_methods()
