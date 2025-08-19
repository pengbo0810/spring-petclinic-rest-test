# src/test/tests_api/test_vets_negative.py
import requests, pytest, allure
from conftest import attach_http

@allure.epic("Vets")
@allure.feature("Validation")
@pytest.mark.parametrize("first,last,specialties,case", [
    ("",              "Auto Bad",    [], "empty firstName"),
    ("Bad_Name_",     "Auto Bad",    [], "illegal char underscore"),
    ("A"*51,          "Auto Long",   [], "too long firstName (51)"),
    ("A B C D",       "Auto Word",   [], "too many parts (>3)"),
])
def test_add_vet_invalid_firstname(base_url, first, last, specialties, case):
    url = f"{base_url}/vets"
    payload = {"firstName": first, "lastName": last, "specialties": specialties}

    with allure.step(f"POST {url} | case: {case}"):
        r = requests.post(url, json=payload, timeout=10)
        attach_http("Add Vet Invalid", url, "POST",
                    {"Content-Type": "application/json"}, payload, r)
        # 预期 400
        assert r.status_code == 400, f"expected 400, got {r.status_code}: {r.text}"
        # 可选：包含字段名的报错（不同版本可能略有差异）
        assert "firstName" in r.text or "Pattern" in r.text or "Validation" in r.text
