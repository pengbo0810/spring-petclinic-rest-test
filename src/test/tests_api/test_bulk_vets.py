# tests_api/test_bulk_vets.py
import os
import random
import string
import requests
import pytest

BASE_URL = os.getenv("PETCLINIC_API", "http://localhost:9966/petclinic/api")
RANDOM_SEED = int(os.getenv("VET_SEED", "20250818"))
random.seed(RANDOM_SEED)

def _rand_letters(n=6):
    # 只用字母，避免下划线/数字触发校验失败
    return "".join(random.choices(string.ascii_letters, k=n)).capitalize()

def _maybe_join(parts):
    """将 1~3 个词用允许的分隔符（空格/连字符/单引号）随机拼接，符合后端正则。"""
    seps = [" ", "-", "'"]
    s = parts[0]
    for p in parts[1:]:
        s += random.choice(seps) + p
    return s

def _fetch_specialties():
    try:
        r = requests.get(f"{BASE_URL}/specialties", timeout=10)
        if r.status_code == 200 and isinstance(r.json(), list):
            return r.json()
    except Exception:
        pass
    return []

def _build_payload(specs_all):
    # firstName：纯字母（或允许的分隔符组合），示例保持简单：单词
    first = _rand_letters()

    # lastName：带一个 “Auto” 前缀 + 随机词，仍然只用允许字符
    last = _maybe_join(["Auto", _rand_letters()])

    # 随机 0~2 个专长
    chosen = []
    if specs_all:
        k = random.randint(0, min(2, len(specs_all)))
        chosen = random.sample(specs_all, k=k)
        chosen = [{"id": s["id"], "name": s.get("name", "")} for s in chosen]

    return {
        "firstName": first,
        "lastName": last,
        "specialties": chosen
    }

def test_bulk_create_20_vets():
    specs_all = _fetch_specialties()
    created_ids = []

    for _ in range(20):
        payload = _build_payload(specs_all)
        resp = requests.post(f"{BASE_URL}/vets", json=payload, timeout=10)
        assert resp.status_code in (200, 201), f"Create failed: {resp.status_code} {resp.text}"
        data = resp.json()
        assert isinstance(data, dict) and "id" in data, f"Unexpected response: {data}"
        created_ids.append(data["id"])

    # 验证都能查到
    get_all = requests.get(f"{BASE_URL}/vets", timeout=10)
    assert get_all.status_code == 200, f"List vets failed: {get_all.status_code} {get_all.text}"
    all_vets = get_all.json()
    ids_in_list = {v.get("id") for v in all_vets if isinstance(v, dict)}
    missing = [vid for vid in created_ids if vid not in ids_in_list]
    assert not missing, f"Created vets not found in list: {missing}"

def test_optional_cleanup_created_vets():
    """
    可选清理：删掉 lastName 里包含 'Auto' 的 Vet。
    如果后端不支持 DELETE /vets/{id}（返回 404/405），直接跳过，不算失败。
    """
    get_all = requests.get(f"{BASE_URL}/vets", timeout=10)
    if get_all.status_code != 200:
        pytest.skip(f"Skip cleanup, list failed: {get_all.status_code}")

    to_delete = [v for v in get_all.json()
                 if isinstance(v, dict) and isinstance(v.get("lastName"), str) and "Auto" in v["lastName"]]

    if not to_delete:
        pytest.skip("No Auto vets to clean")

    for v in to_delete:
        vid = v.get("id")
        if vid is None:
            continue
        resp = requests.delete(f"{BASE_URL}/vets/{vid}", timeout=10)
        if resp.status_code in (200, 204):
            continue
        elif resp.status_code in (404, 405):
            pytest.skip(f"DELETE not supported or vet not found (id={vid}): {resp.status_code}")
        else:
            pytest.fail(f"Delete vet {vid} failed: {resp.status_code} {resp.text}")
