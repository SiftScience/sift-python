import sift

from os import environ as env


class WorkflowsAPI():
    # Get the value of API_KEY from environment variable
    api_key = env['API_KEY']
    client = sift.Client(api_key = api_key)
    
    def synchronous_workflows(self):
        properties = {
            '$user_id'    : 'test_user',
            '$user_email' : 'sample_user@gmail.com'
        } 
        return self.client.track('$create_order', properties, return_workflow_status=True, 
                                return_route_info=True, abuse_types=['promo_abuse', 'content_abuse', 'payment_abuse'])


