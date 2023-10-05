import sift
import globals
from os import environ as env

class WorkflowsAPI():
    # Get the value of API_KEY from environment variable
    api_key = env['API_KEY']
    client = sift.Client(api_key = api_key)
    globals.initialize()
    user_id = globals.user_id
    user_email = globals.user_email
    
    def synchronous_workflows(self):
        properties = {
            '$user_id'    : self.user_id,
            '$user_email' : self.user_email
        } 
        return self.client.track('$create_order', properties, return_workflow_status=True, 
                                return_route_info=True, abuse_types=['promo_abuse', 'content_abuse', 'payment_abuse'])
        