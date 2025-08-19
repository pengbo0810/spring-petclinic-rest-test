import requests, pytest, allure
from conftest import attach_http   # 注意这行用绝对导入

CASES = [
    ({"date":"2025-13-01", "description":"Bad date", "pet":{"id":1}}, "invalid month"),
    ({"date":"2025-01-01", "description":"No pet"},                    "missing pet"),
    ({"date":"",           "description":"Empty date", "pet":{"id":1}},"empty date"),
    ({"date":"2025-01-01", "description":"",           "pet":{"id":1}},"empty description"),
]

# 根据用例名设置预期状态码集合
EXPECTED = {
    "invalid month": {400, 500},   # 反序列化失败：有的环境是400，有的是500
    "missing pet": {400},
    "empty date": {400},
    "empty description": {400},
}

@allure.epic("Visits")
@allure.feature("Validation")
@pytest.mark.parametrize("payload,case", CASES, ids=[c for _, c in CASES])
def test_add_visit_invalid(base_url, payload, case):
    url = f"{base_url}/visits"
    with allure.step(f"POST {url} | case: {case}"):
        r = requests.post(url, json=payload, timeout=10)
        attach_http("Add Visit Invalid", url, "POST",
                    {"Content-Type": "application/json"}, payload, r)

        assert r.status_code in EXPECTED[case], f"{case}: expected {EXPECTED[case]}, got {r.status_code}: {r.text}"

        # 针对反序列化失败，再做一条语义校验，增强可读性
        if case == "invalid month":
            assert ("DateTimeParseException" in r.text) or ("Cannot deserialize value of type" in r.text)
