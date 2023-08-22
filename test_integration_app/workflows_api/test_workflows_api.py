import sift

from os import environ as env
 # Get the value of API_KEY from environment variable
api_key = env['API_KEY']
client = sift.Client(api_key = api_key)

def get_workflow_status(workflow_run_id):
    response = client.get_workflow_status(workflow_run_id)
    assert(response.is_ok())
    assert response.api_status == 0, "api_status should be 0"
    assert response.api_error_message == "OK", "api_error_message should be OK"


