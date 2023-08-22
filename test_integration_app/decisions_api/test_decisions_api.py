import sift

from os import environ as env
 # Get the value of API_KEY from environment variable
api_key = env['API_KEY']
account_id = env['ACCT']
client = sift.Client(api_key = api_key, account_id = account_id)


def apply_user_decision():
    applyDecisionRequest = {
        "decision_id"     : "block_user_payment_abuse",
        "source"          : "MANUAL_REVIEW",
        "analyst"         : "haneeshv@exalture.com",
        "description"     : "User linked to three other payment abusers and ordering high value items"
    }
    
    response = client.apply_user_decision("haneeshv@exalture.com", applyDecisionRequest)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def apply_order_decision():
    applyOrderDecisionRequest = {
        "decision_id"   : "block_order_payment_abuse",
        "source"    : "AUTOMATED_RULE",
        "description"   : "Auto block pending order as score exceeded risk threshold of 90"
    }
    
    response = client.apply_order_decision("haneeshv@exalture.com", "ORDER-1234567", applyOrderDecisionRequest)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def apply_session_decision():
    applySessionDecisionRequest = {
        "decision_id"   : "session_looks_fraud_account_takover",
        "source"    : "MANUAL_REVIEW",
        "analyst"   : "analyst@example.com",
        "description"   : "compromised account reported to customer service"
    }
    
    response = client.apply_session_decision('haneeshv@exalture.com', "session_id", applySessionDecisionRequest)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def apply_content_decision():
    applyContentDecisionRequest = {
        "decision_id"    : "content_looks_fraud_content_abuse",
        "source"         : "MANUAL_REVIEW",
        "analyst"       : "analyst@example.com",
        "description"    : "fraudulent listing"
    }
    
    response = client.apply_content_decision('haneeshv@exalture.com', "content_id", applyContentDecisionRequest)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def get_user_decisions():
    response = client.get_user_decisions("haneeshv@exalture.com")
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def get_order_decisions():
    response = client.get_order_decisions("ORDER-1234567")
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def get_content_decisions():
    response = client.get_content_decisions("haneeshv@exalture.com", "CONTENT_ID")
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def get_session_decisions():
    response = client.get_session_decisions("haneeshv@exalture.com", "SESSION_ID")
    print(response)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"
    
def get_decisions(entityType):
    response = client.get_decisions(entityType)
    print(response)
    assert(response.is_ok())
    assert response.http_status_code == 200, "api_status should be 200"
