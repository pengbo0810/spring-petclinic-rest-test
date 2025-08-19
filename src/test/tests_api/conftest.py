import os, time, json, requests, pytest, allure

BASE_URL = os.getenv("PETCLINIC_API", "http://localhost:9966/petclinic/api")

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session", autouse=True)
def wait_petclinic_up():
    url = f"{BASE_URL}/vets"
    for _ in range(60):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    pytest.skip(f"PetClinic REST not reachable: {url}")

def attach_json(name: str, data):
    try:
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2),
                      name=name, attachment_type=allure.attachment_type.JSON)
    except Exception:
        allure.attach(str(data), name=name, attachment_type=allure.attachment_type.TEXT)

def attach_http(name: str, url: str, method: str, headers: dict | None, body, resp: requests.Response | None):
    # 请求
    req = {
        "method": method,
        "url": url,
        "headers": headers or {},
        "body": body
    }
    attach_json(f"{name} - Request", req)
    # 响应
    if resp is not None:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        res = {
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "body": body
        }
        attach_json(f"{name} - Response", res)