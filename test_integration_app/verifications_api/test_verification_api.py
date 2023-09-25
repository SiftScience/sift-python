import sift

from os import environ as env

class VerificationAPI():
    # Get the value of API_KEY from environment variable
    api_key = env['API_KEY']
    client = sift.Client(api_key = api_key)
    
    def send(self):
        sendProperties = {
            '$user_id': 'billy_jones_301',
            '$send_to': 'billy_jones_301@gmail.com',
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
        return self.client.verification_send(sendProperties)
            
    def resend(self):    
        resendProperties = {
            '$user_id': 'billy_jones_301',
            '$verified_event': '$login',
            '$verified_entity_id': 'SOME_SESSION_ID'
        } 
        return self.client.verification_resend(resendProperties)

    def check(self):
        checkProperties = {
            '$user_id': 'billy_jones_301',
            '$code': '123456',
            '$verified_event': '$login',
            '$verified_entity_id': "SOME_SESSION_ID"
        }
        return self.client.verification_check(checkProperties)

