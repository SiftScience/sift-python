from decimal import Decimal
import sift
import sys

if sys.version_info[0] < 3:
    import six.moves.urllib as urllib 
else:
    import urllib.parse

def response_with_data_header():
    return {
        'content-type': 'application/json; charset=UTF-8'
    }

sendProperties = {
  '$user_id'          : 'haneeshv@exalture.com',
  '$send_to'          :	'haneeshv@exalture.com',
  '$verification_type': '$email',
  '$brand_name'       : 'MyTopBrand',
  '$language'         : 'en',
  "$site_country": "IN",
  '$event': {
      '$session_id': 'SOME_SESSION_ID',
      # '$verified_event': '$login',
      '$verified_entity_id': 'SOME_SESSION_ID',
      '$reason': '$automated_rule',
      '$ip': '192.168.1.1',
      '$browser': {
          '$user_agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
      }
  }
}

resendProperties = {
  '$user_id'          : 'haneeshv@exalture.com',
  '$verified_event': '$login',
  '$verified_entity_id': 'SOME_SESSION_ID'
} 

checkProperties = {
  '$user_id'          : 'haneeshv@exalture.com',
  '$code'          :	'636068',
  '$verified_event': '$login',
  '$verified_entity_id' : "SOME_SESSION_ID"
} 

def test_verification_send():
  client = sift.Client(api_key='valid-api-key', account_id='ACCT')
  response = client.verification_send(sendProperties)
  print(response)
     
def test_verification_resend():
  client = sift.Client(api_key='valid-api-key', account_id='ACCT')
  response = client.verification_resend(resendProperties)
  print(response)

def test_verification_check():
  client = sift.Client(api_key='valid-api-key', account_id='ACCT')
  response = client.verification_check(checkProperties)
  print(response)

test_verification_send()

# test_verification_resend()

# test_verification_check()
