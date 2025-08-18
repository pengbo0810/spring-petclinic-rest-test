import requests

BASE_URL = "http://localhost:9966/petclinic/api"

def test_get_vets():
    res = requests.get(f"{BASE_URL}/vets")
    assert res.status_code == 200
    
    data = res.json()
    # 确认 data 是 list
    assert isinstance(data, list)
    # 确认至少有一个医生
    assert len(data) > 0
    # 确认医生数据结构正确
    first_vet = data[0]
    assert "id" in first_vet
    assert "firstName" in first_vet
    assert "lastName" in first_vet
    assert "specialties" in first_vet