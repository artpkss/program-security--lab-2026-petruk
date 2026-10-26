import hmac
import hashlib
import os

class IntegrityService:
    def __init__(self, secret_key: bytes = None):
        self.secret_key = secret_key or os.urandom(32)

    def sign_data(self, data: str) -> str:
        """Формування коду автентичності (HMAC-SHA256)."""
        return hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256).hexdigest()

    def verify_data(self, data: str, expected_hmac: str) -> bool:
        """Перевірка цілісності та автентичності даних."""
        actual_hmac = self.sign_data(data)
        return hmac.compare_digest(actual_hmac, expected_hmac)

if __name__ == "__main__":
    print("=== ТЕСТУВАННЯ СЕРВІСУ КОНТРОЛЮ ЦІЛІСНОСТІ СИСТЕМИ ===")
    service = IntegrityService()
    
    # Штатна сценарій
    payload = "user_id=101&role=user&action=transfer"
    signature = service.sign_data(payload)
    print(f"Дані: {payload}")
    print(f"HMAC підпис: {signature}")
    
    is_valid = service.verify_data(payload, signature)
    print(f"Штатна перевірка: {'✅ ПЕРЕВІРКУ ПРОЙДЕНО' if is_valid else '❌ ПОМИЛКА'}")
    
    # Навмисна модифікація даних зловмисником
    tampered_payload = "user_id=101&role=admin&action=transfer"
    is_tampered_valid = service.verify_data(tampered_payload, signature)
    print(f"\nМодифіковані дані: {tampered_payload}")
    print(f"Перевірка модифікованих даних: {'✅ ПЕРЕВІРКУ ПРОЙДЕНО' if is_tampered_valid else '❌ [АТАКА ВИЯВЛЕНА] Відмова в обробці!'}")
