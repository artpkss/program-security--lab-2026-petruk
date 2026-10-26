import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureSymmetricCrypto:
    def __init__(self, key: bytes = None):
        # 256-бітний ключ шифрування
        self.key = key or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.key)

    def encrypt_data(self, plaintext: str) -> dict:
        """Автентифіковане шифрування AES-GCM."""
        nonce = os.urandom(12)  # Унікальний 96-бітний nonce
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return {
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex()
        }

    def decrypt_data(self, nonce_hex: str, ciphertext_hex: str) -> str:
        """Розшифрування та перевірка автентичності/цілісності."""
        nonce = bytes.fromhex(nonce_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        decrypted = self.aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode('utf-8')

if __name__ == "__main__":
    print("=== ТЕСТУВАННЯ АВТЕНТИФІКОВАНОГО ШИФРУВАННЯ AES-GCM ===")
    service = SecureSymmetricCrypto()
    
    secret_data = "Чудово! Чутливі дані користувача petruk під надійним захистом AES-GCM."
    encrypted = service.encrypt_data(secret_data)
    print(f"Зашифровано: {encrypted['ciphertext'][:30]}...")
    
    decrypted = service.decrypt_data(encrypted["nonce"], encrypted["ciphertext"])
    print(f"Розшифровано: {decrypted}")
