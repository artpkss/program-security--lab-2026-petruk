#!/usr/bin/env python3
import json
import sys
import urllib.error
import urllib.request

# Налаштування UTF-8 для коректного виведення кирилиці у терміналі Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8080"

# Замініть на дані вашого варіанта з Додатку А (зараз стоїть Варіант 1)
CLIENT_ID = "rose-01"
CLIENT_SECRET = "A7mQ2pL9xR4v"


class LibraryClient:
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def authenticate(self) -> None:
        """Отримує та зберігає токен доступу через POST /auth/token."""
        url = f"{self.base_url}/auth/token"
        payload = json.dumps({
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            self.access_token = data.get("access_token")
            expires = data.get("expires_in", "невідомо")
            print(f"[+] Автентифікація успішна! Токен отримано (діє {expires} сек).\n")

    def get_protected(self, endpoint: str):
        """Виконує GET-запит до захищеного маршруту із заголовком Bearer."""
        if not self.access_token:
            raise RuntimeError("Спочатку потрібно виконати authenticate().")

        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            },
            method="GET"
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))


def main():
    client = LibraryClient(BASE_URL, CLIENT_ID, CLIENT_SECRET)

    try:
        # 1. Отримання токена
        client.authenticate()

        # 2. Профіль поточного читача
        profile = client.get_protected("/whoami")
        print("=== 1. ДАНІ ЧИТАЧА (/whoami) ===")
        print(json.dumps(profile, ensure_ascii=False, indent=2), "\n")

        # 3. Список доступних книг
        books_data = client.get_protected("/api/books")
        print("=== 2. СПИСОК КНИГ (/api/books) ===")
        print(json.dumps(books_data, ensure_ascii=False, indent=2), "\n")

        # 4. Детальна інформація про першу книгу зі списку
        books_list = books_data.get("books", []) if isinstance(books_data, dict) else books_data
        if books_list and isinstance(books_list[0], dict):
            book_id = books_list[0].get("id")
            if book_id is not None:
                book_detail = client.get_protected(f"/api/books/{book_id}")
                print(f"=== 3. ДЕТАЛІ КНИГИ ID={book_id} (/api/books/{book_id}) ===")
                print(json.dumps(book_detail, ensure_ascii=False, indent=2), "\n")

        # 5. Активні позики читача
        loans = client.get_protected("/api/loans")
        print("=== 4. АКТИВНІ ПОЗИКИ (/api/loans) ===")
        print(json.dumps(loans, ensure_ascii=False, indent=2), "\n")

        # 6. Зведена статистика
        summary = client.get_protected("/api/summary")
        print("=== 5. ЗВЕДЕНА ІНФОРМАЦІЯ (/api/summary) ===")
        print(json.dumps(summary, ensure_ascii=False, indent=2), "\n")

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[!] Помилка від сервера (HTTP {e.code}):\n{body}")
    except urllib.error.URLError:
        print("[!] Помилка з'єднання: сервер не запущений на http://127.0.0.1:8080.")
        print("    Запустіть у сусідньому терміналі: python lab6_library_server.py")


if __name__ == "__main__":
    main()