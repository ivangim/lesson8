import os
import requests
from dotenv import load_dotenv

load_dotenv()


class CompanyApi:
    def __init__(self, base_url: str = "https://ru.yougile.com"):
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None

    def get_token(self, company_id: str | None = None) -> str:
        if self._token:
            return self._token

        login = os.getenv("YOUGILE_LOGIN")
        password = os.getenv("YOUGILE_PASSWORD")
        company_id = company_id or os.getenv("YOUGILE_COMPANY_ID")

        missing = []
        if not login:
            missing.append("YOUGILE_LOGIN")
        if not password:
            missing.append("YOUGILE_PASSWORD")

        if missing:
            raise ValueError(f"Не заданы переменные окружения: {', '.join(missing)}")

        url = f"{self.base_url}/api-v2/auth/keys"
        payload = {"login": login, "password": password}
        if company_id:
            payload["companyId"] = company_id

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка запроса к YouGile: {e}") from e

        if isinstance(data, list):
            if not data:
                raise ValueError("Сервер вернул пустой список ключей.")
            latest = max(data, key=lambda k: k.get("timestamp", 0))
        elif isinstance(data, dict) and "key" in data:
            latest = data
        else:
            raise ValueError(f"Неожиданный формат ответа: {data}")

        key = latest.get("key")
        if not key:
            raise ValueError(f"В ответе нет поля 'key': {latest}")

        self._token = key
        return self._token

    def token(self) -> str | None:
        return self._token

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        if self._token is None:
            raise RuntimeError("Токен не установлен. Вызовите get_token() сначала.")
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        return requests.request(method, url, headers=headers, **kwargs)