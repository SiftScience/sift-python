import sift

from os import environ as env
 # Get the value of API_KEY from environment variable
api_key = env['API_KEY']
account_id = env['ACCT']
client = sift.Client(api_key = api_key, account_id = account_id)

def create_merchant():
  merchantProperties={
    "id": "merchant_id_01013",
    "name": "Wonderful Payments Inc.13",
    "description": "Wonderful Payments payment provider.",
    "address": {
      "name": "Alany",
      "address_1": "Big Payment blvd, 22",
      "address_2": "apt, 8",
      "city": "New Orleans",
      "region": "NA",
      "country": "US",
      "zipcode": "76830",
      "phone": "0394888320"
    },
    "category": "1002",
    "service_level": "Platinum",
    "status": "active",
    "risk_profile": {
      "level": "low",
      "score": 10
    }
  }
  response = client.create_psp_merchant_profile(merchantProperties)
  print(response)
  assert response.http_status_code == 201, "api_status should be 201"
  
def edit_merchant():
  merchantProperties={
    "id": "merchant_id_01013",
    "name": "Wonderful Payments Inc.13 edit",
    "description": "Wonderful Payments payment provider. edit",
    "address": {
      "name": "Alany",
      "address_1": "Big Payment blvd, 22",
      "address_2": "apt, 8",
      "city": "New Orleans",
      "region": "NA",
      "country": "US",
      "zipcode": "76830",
      "phone": "0394888320"
    },
    "category": "1002",
    "service_level": "Platinum",
    "status": "active",
    "risk_profile": {
      "level": "low",
      "score": 10
    }
  }
  response = client.update_psp_merchant_profile("merchant_id_01013", merchantProperties)
  print(response)
  assert response.http_status_code == 200, "api_status should be 200"

def get_a_merchant_profile():
  response = client.get_a_psp_merchant_profile("merchant_id_01013")
  print(response)
  assert response.http_status_code == 200, "api_status should be 200"

def get_merchant_profiles():
  response = client.get_psp_merchant_profiles()
  print(response)
  assert response.http_status_code == 200, "api_status should be 200"

def get_merchant_profiles(batch_token = None, batch_size = None):
  response = client.get_psp_merchant_profiles(batch_token, batch_size)
  print(response)
  assert response.http_status_code == 200, "api_status should be 200"