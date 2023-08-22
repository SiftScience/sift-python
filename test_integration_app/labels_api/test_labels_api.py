import sift

from os import environ as env
 # Get the value of API_KEY from environment variable
api_key = env['API_KEY']
client = sift.Client(api_key = api_key)

def user_label(): 
  properties = {
    "$is_fraud"      : True, # ... or False; Required 
    "$abuse_type"  : "payment_abuse", # Required
    "$description" : "The user was testing cards repeatedly for a valid card", # Optional
    "$source"      : "manual review", # Optional
    "$analyst"     : "someone@your-site.com" # Optional
    }
  response = client.label("haneeshv@exalture.com", properties)
  print(response)
  assert(response.is_ok())
  assert response.api_status == 0, "api_status should be 0"
  assert response.api_error_message == "OK", "api_error_message should be OK"

def user_unlabel(): 
  response = client.unlabel("haneeshv@exalture.com", abuse_type = "payment_abuse")
  print(response)
  assert(response.is_ok())
  assert response.http_status_code == 204, "api_status should be 204"
