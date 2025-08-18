import requests

def test_get_pettypes(base_url):
    res = requests.get(f"{base_url}/pettypes")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert "id" in data[0]

def test_add_pet(base_url):
    owner_id = 1  # 假设数据库已有主人
    payload = {
        "name": "Fluffy",
        "birthDate": "2020-01-01",
        "type": {"id": 1, "name": "cat"},
        "owner": {"id": owner_id}
    }
    res = requests.post(f"{base_url}/owners/{owner_id}/pets", json=payload)
    assert res.status_code in (201, 200)
