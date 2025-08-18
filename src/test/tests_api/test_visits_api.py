# tests_api/test_visits_api.py
import requests
import datetime as dt

BASE_DATE = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y-%m-%d")

def _create_owner(base_url):
    payload = {
        "firstName": "Visit",
        "lastName": "Owner",
        "address": "1 Test St",
        "city": "TestCity",
        "telephone": "1234567890"
    }
    r = requests.post(f"{base_url}/owners", json=payload)
    assert r.status_code in (200, 201), f"Create owner failed: {r.status_code} {r.text}"
    return r.json()["id"]

def _create_pet(base_url, owner_id):
    # 选一个合法的 pet type（先查 /pettypes）
    types = requests.get(f"{base_url}/pettypes").json()
    assert isinstance(types, list) and len(types) > 0, "No pet types found"
    pet_type = types[0]  # 取第一个类型

    payload = {
        "name": "API-Pet",
        "birthDate": "2022-01-01",
        "type": {"id": pet_type["id"], "name": pet_type.get("name", "")},
        "owner": {"id": owner_id}
    }
    r = requests.post(f"{base_url}/owners/{owner_id}/pets", json=payload)
    assert r.status_code in (200, 201), f"Create pet failed: {r.status_code} {r.text}"
    return r.json()["id"]

def test_get_visits(base_url):
    r = requests.get(f"{base_url}/visits")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_add_visit(base_url):
    owner_id = _create_owner(base_url)
    pet_id = _create_pet(base_url, owner_id)

    # 一些版本要求 body 是 {"date": "...", "description": "...", "pet": {"id": <id>}}
    # 也有版本接受 {"date": "...", "description": "...", "petId": <id>}
    # 先用官方常见的嵌套 pet 写法；若失败，回退为 petId 写法。
    payload = {
        "date": BASE_DATE,                # 用明天的日期，避免过去日期被拒
        "description": "Regular Checkup",
        "pet": {"id": pet_id}
    }
    res = requests.post(f"{base_url}/visits", json=payload)
    if res.status_code == 400:
        # 尝试兼容另一种 schema（petId）
        payload_alt = {
            "date": BASE_DATE,
            "description": "Regular Checkup",
            "petId": pet_id
        }
        res = requests.post(f"{base_url}/visits", json=payload_alt)

    assert res.status_code in (200, 201), f"Create visit failed: {res.status_code} {res.text}"
    data = res.json()
    # 基本字段校验
    assert "id" in data
    assert data.get("description") == "Regular Checkup"
