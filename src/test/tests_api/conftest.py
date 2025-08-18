import pytest

BASE_URL = "http://localhost:9966/petclinic/api"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL