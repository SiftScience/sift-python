import sift
import globals

from os import environ as env

class DecisionAPI():
    # Get the value of API_KEY from environment variable
    api_key = env['API_KEY']
    account_id = env['ACCOUNT_ID']
    client = sift.Client(api_key = api_key, account_id = account_id)
    globals.initialize()
    user_id = globals.user_id

    def apply_user_decision(self):
        applyDecisionRequest = {
            "decision_id"     : "block_user_payment_abuse",
            "source"          : "MANUAL_REVIEW",
            "analyst"         : "analyst@example.com",
            "description"     : "User linked to three other payment abusers and ordering high value items"
        }
        
        return self.client.apply_user_decision(self.user_id, applyDecisionRequest)

    def apply_order_decision(self):
        applyOrderDecisionRequest = {
            "decision_id"   : "block_order_payment_abuse",
            "source"    : "AUTOMATED_RULE",
            "description"   : "Auto block pending order as score exceeded risk threshold of 90"
        }
        
        return self.client.apply_order_decision(self.user_id, "ORDER-1234567", applyOrderDecisionRequest)

    def apply_session_decision(self):
        applySessionDecisionRequest = {
            "decision_id"   : "session_looks_fraud_account_takover",
            "source"    : "MANUAL_REVIEW",
            "analyst"   : "analyst@example.com",
            "description"   : "compromised account reported to customer service"
        }
        
        return self.client.apply_session_decision(self.user_id, "session_id", applySessionDecisionRequest)

    def apply_content_decision(self):
        applyContentDecisionRequest = {
            "decision_id"    : "content_looks_fraud_content_abuse",
            "source"         : "MANUAL_REVIEW",
            "analyst"       : "analyst@example.com",
            "description"    : "fraudulent listing"
        }
        
        return self.client.apply_content_decision(self.user_id, "content_id", applyContentDecisionRequest)

    def get_user_decisions(self):
        return self.client.get_user_decisions(self.user_id)

    def get_order_decisions(self):
        return self.client.get_order_decisions("ORDER-1234567")

    def get_content_decisions(self):
        return self.client.get_content_decisions(self.user_id, "CONTENT_ID")

    def get_session_decisions(self):
        return self.client.get_session_decisions(self.user_id, "SESSION_ID")
        
    def get_decisions(self):
        return self.client.get_decisions(entity_type='user', limit=10, start_from=5, abuse_types='legacy,payment_abuse')
