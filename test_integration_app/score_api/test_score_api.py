import sift
import globals

from os import environ as env

class ScoreAPI(): 
  # Get the value of API_KEY from environment variable
  api_key = env['API_KEY']
  client = sift.Client(api_key = api_key)
  globals.initialize()
  user_id = globals.user_id
  
  def get_user_score(self):
    return self.client.get_user_score(user_id = self.user_id, abuse_types=["payment_abuse", "promotion_abuse"])
