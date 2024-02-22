import requests

test_api_key = "UgK3u/eHN6X8UrhwJRSIUT51rLrcJymTK6oHjwvYBlo="
test_api_password = "d_yTqtIfhn]g7V5A[v==Vp"


def authenticate(customer_id):
    r = requests.post("https://test.paygiga.com/api/transaction/authenticate", data={
        "merchantKey": test_api_key,
        "merchantPassword": test_api_password,
        "customerId": customer_id
    })
    return r.json()


def get_bank_list(customer_id):
    session_id = authenticate(customer_id).get("session_id")
    r = requests.post("https://test.paygiga.com/api/getBankList", data={
        "session_id": session_id,
        "aim": "deposit"
    })


print(get_bank_list("12345"))
