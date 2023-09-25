import sift
import string 
import random # define the random module  

from os import environ as env


class PSPMerchantAPI():
  # Get the value of API_KEY and ACCOUNT_ID from environment variable
  api_key = env['API_KEY']
  account_id = env['ACCT']

  client = sift.Client(api_key = api_key, account_id = account_id)
  
  def create_merchant(self):
    merchant_id = ''.join(random.choices(string.digits, k = 7))    
    merchantProperties={
      "id": 'merchant_id_' + merchant_id,
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
    return self.client.create_psp_merchant_profile(merchantProperties)
    
  def edit_merchant(self):
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
    return self.client.update_psp_merchant_profile("merchant_id_01013", merchantProperties)

  def get_a_merchant_profile(self):
    return self.client.get_a_psp_merchant_profile("merchant_id_01013")

  def get_merchant_profiles(self, batch_token = None, batch_size = None):
    return self.client.get_psp_merchant_profiles(batch_token, batch_size)
  
  