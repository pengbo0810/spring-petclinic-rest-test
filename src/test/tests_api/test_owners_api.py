import requests

def test_get_owners(base_url):
    res = requests.get(f"{base_url}/owners")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert "id" in data[0]

def test_add_owner(base_url):
    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "address": "123 Main St",
        "city": "New York",
        "telephone": "1234567890"
    }
    res = requests.post(f"{base_url}/owners", json=payload)
    assert res.status_code in (201, 200)
    data = res.json()
    assert "id" in data
