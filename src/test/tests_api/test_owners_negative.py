# src/test/tests_api/test_owners_negative.py
import requests, pytest, allure
from conftest import attach_http

@allure.epic("Owners")
@allure.feature("Validation")
@pytest.mark.parametrize("payload,case", [
    ({"firstName":"", "lastName":"Doe", "address":"1 St", "city":"NY", "telephone":"1234567890"}, "empty firstName"),
    ({"firstName":"John","lastName":"", "address":"1 St", "city":"NY", "telephone":"1234567890"}, "empty lastName"),
    ({"firstName":"John","lastName":"Doe","address":"",   "city":"NY", "telephone":"1234567890"}, "empty address"),
    ({"firstName":"John","lastName":"Doe","address":"1 St","city":"", "telephone":"1234567890"}, "empty city"),
    ({"firstName":"John","lastName":"Doe","address":"1 St","city":"NY","telephone":"abc"},       "non-digit telephone"),
    ({"firstName":"John","lastName":"Doe","address":"1 St","city":"NY","telephone":""},          "empty telephone"),
])
def test_add_owner_invalid_payload(base_url, payload, case):
    url = f"{base_url}/owners"
    with allure.step(f"POST {url} | case: {case}"):
        r = requests.post(url, json=payload, timeout=10)
        attach_http("Add Owner Invalid", url, "POST",
                    {"Content-Type": "application/json"}, payload, r)
        assert r.status_code == 400, f"expected 400, got {r.status_code}: {r.text}"
