import sift

from os import environ as env
 # Get the value of API_KEY from environment variable
api_key = env['API_KEY']
client = sift.Client(api_key = api_key)


def test_verification_send():
    sendProperties = {
        '$user_id': 'haneeshv@exalture.com',
        '$send_to': 'haneeshv@exalture.com',
        '$verification_type': '$email',
        '$brand_name': 'MyTopBrand',
        '$language': 'en',
        '$site_country': 'IN',
        '$event': {
            '$session_id': 'SOME_SESSION_ID',
            '$verified_event': '$login',
            '$verified_entity_id': 'SOME_SESSION_ID',
            '$reason': '$automated_rule',
            '$ip': '192.168.1.1',
            '$browser': {
                '$user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                '$accept_language': 'en-US',
                '$content_language': 'en-GB'
            }
        }
    }
    
    response = client.verification_send(sendProperties)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"
        
def test_verification_resend():    
    resendProperties = {
        '$user_id': 'haneeshv@exalture.com',
        '$verified_event': '$login',
        '$verified_entity_id': 'SOME_SESSION_ID'
    } 

    response = client.verification_resend(resendProperties)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"

def test_verification_check(code):
    checkProperties = {
        '$user_id': 'haneeshv@exalture.com',
        '$code': code,
        '$verified_event': '$login',
        '$verified_entity_id': "SOME_SESSION_ID"
    }

    response = client.verification_check(checkProperties)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"
