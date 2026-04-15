import requests


class OrionLDClient:
    def __init__(self, host="localhost", port=1026):
        self.base_url = f"http://{host}:{port}"
        self.headers = {"Content-Type": "application/ld+json"}

    def upsert(self, entity: dict) -> bool:
        url = f"{self.base_url}/ngsi-ld/v1/entityOperations/upsert"
        resp = requests.post(url, headers=self.headers, json=[entity], timeout=10)
        return resp.status_code in (200, 201, 204)

    def query(self, entity_type: str, limit=100) -> list:
        url = f"{self.base_url}/ngsi-ld/v1/entities"
        params = {"type": entity_type, "limit": limit}
        resp = requests.get(url, headers=self.headers, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else []

    def delete(self, entity_id: str) -> bool:
        url = f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}"
        resp = requests.delete(url, timeout=10)
        return resp.status_code == 204

    def healthy(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/version", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
