import requests

def test_get_vets(base_url):
    res = requests.get(f"{base_url}/vets")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    vet = data[0]
    assert "id" in vet and "firstName" in vet and "lastName" in vet

def test_add_vet(base_url):
    payload = {
        "firstName": "Test",
        "lastName": "Doctor",
        "specialties": []
    }
    res = requests.post(f"{base_url}/vets", json=payload)
    assert res.status_code in (201, 200)