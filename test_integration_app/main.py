from verifications_api import test_verification_api

def test_send():
    test_verification_api.test_verification_send()

def test_resend():
    test_verification_api.test_verification_resend()

def test_check(code):
    test_verification_api.test_verification_check(code)

test_send()

# test_resend()

# test_check(329311)