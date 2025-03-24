from os import environ as env

import globals

import sift


class DecisionAPI:
    # Get the value of API_KEY from environment variable
    api_key = env["API_KEY"]
    account_id = env["ACCOUNT_ID"]
    client = sift.Client(api_key=api_key, account_id=account_id)
    globals.initialize()
    user_id = globals.user_id
    session_id = globals.session_id

    def apply_user_decision(self) -> sift.client.Response:
        properties = {
            "decision_id": "integration_app_watch_account_abuse",
            "source": "MANUAL_REVIEW",
            "analyst": "analyst@example.com",
            "description": "User linked to three other payment abusers and ordering high value items",
        }

        return self.client.apply_user_decision(self.user_id, properties)

    def apply_order_decision(self) -> sift.client.Response:
        properties = {
            "decision_id": "block_order_payment_abuse",
            "source": "AUTOMATED_RULE",
            "description": "Auto block pending order as score exceeded risk threshold of 90",
        }

        return self.client.apply_order_decision(
            self.user_id, "ORDER-1234567", properties
        )

    def apply_session_decision(self) -> sift.client.Response:
        properties = {
            "decision_id": "integration_app_watch_account_takeover",
            "source": "MANUAL_REVIEW",
            "analyst": "analyst@example.com",
            "description": "compromised account reported to customer service",
        }

        return self.client.apply_session_decision(
            self.user_id, self.session_id, properties
        )

    def apply_content_decision(self) -> sift.client.Response:
        properties = {
            "decision_id": "integration_app_watch_content_abuse",
            "source": "MANUAL_REVIEW",
            "analyst": "analyst@example.com",
            "description": "fraudulent listing",
        }

        return self.client.apply_content_decision(
            self.user_id, "content_id", properties
        )

    def get_user_decisions(self) -> sift.client.Response:
        return self.client.get_user_decisions(self.user_id)

    def get_order_decisions(self) -> sift.client.Response:
        return self.client.get_order_decisions("ORDER-1234567")

    def get_content_decisions(self) -> sift.client.Response:
        return self.client.get_content_decisions(self.user_id, "CONTENT_ID")

    def get_session_decisions(self) -> sift.client.Response:
        return self.client.get_session_decisions(self.user_id, "SESSION_ID")

    def get_decisions(self) -> sift.client.Response:
        return self.client.get_decisions(
            entity_type="user",
            limit=10,
            start_from=5,
            abuse_types="legacy,payment_abuse",
        )
