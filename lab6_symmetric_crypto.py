import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# 2. Формування початкового текстового рядка (варіант 01)
# Формат: [поточний_рік]_[група]_[прізвище]_[ім'я]_варіант:[номер]
pt1 = "2026_IP81_petruk_artem_variant:01".encode('utf-8')

# 3. Генеруємо випадковий Ключ №1 (256 біт) та Вектор ініціалізації (128 біт)
key1 = os.urandom(32)
iv1 = os.urandom(16)

# 4. Шифрування AES у режимі CTR -> Шифротекст №1
cipher1 = Cipher(algorithms.AES(key1), modes.CTR(iv1), backend=default_backend())
encryptor1 = cipher1.encryptor()
ct1 = encryptor1.update(pt1) + encryptor1.finalize()

print("=== РЕЗУЛЬТАТИ ШИФРУВАННЯ (AES-CTR) ===")
print(f"Відкритий текст №1: {pt1.decode()}")
print(f"Ключ №1 (HEX):       {key1.hex()}")
print(f"Вектор №1 (HEX):     {iv1.hex()}")
print(f"Шифротекст №1 (HEX): {ct1.hex()}\n")

# 5. Атака на основі відомого відкритого тексту (Known-Plaintext Attack)
# 5.2. Відновлення Гами №1 через XOR шифротексту та відкритого тексту
keystream1 = bytes([b1 ^ b2 for b1, b2 in zip(ct1, pt1)])
print(f"Відновлена Гама №1 (HEX): {keystream1.hex()}")

# 5.3. Новий рядок з варіантом 99
pt2 = "2026_IP81_petruk_artem_variant:99".encode('utf-8')

# 5.4. Генерація Шифротексту №2 шляхом XOR Гами №1 з альтернативним текстом
ct2 = bytes([b1 ^ b2 for b1, b2 in zip(keystream1, pt2)])
print(f"Альтернативний текст №2:  {pt2.decode()}")
print(f"Сформований Шифротекст №2: {ct2.hex()}\n")

# 6. Перевірка: Розшифрування Шифротексту №2 за допомогою оригінального Ключа №1 і Вектора №1
cipher2 = Cipher(algorithms.AES(key1), modes.CTR(iv1), backend=default_backend())
decryptor2 = cipher2.decryptor()
decrypted2 = decryptor2.update(ct2) + decryptor2.finalize()

print("=== РЕЗУЛЬТАТ РОЗШИФРУВАННЯ ЗЛОВМИСНИЦЬКОГО ШИФРОТЕКСТУ ===")
print(f"Розшифрований результат: {decrypted2.decode()}")
