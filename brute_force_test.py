import time
import hashlib
import bcrypt

# 9. Створення базового рядка
target_password = "pass: petruk"

# 10. Словник із 20 кандидатів (правильний пароль — на останній, 20-й позиції)
dictionary = [f"wrong_password_{i}" for i in range(1, 20)] + [target_password]

# 11. Хеш SHA-256 (Хеш №5)
hash_sha256 = hashlib.sha256(target_password.encode('utf-8')).hexdigest()

# 12. Хеш bcrypt (rounds=12, Хеш №6)
hash_bcrypt = bcrypt.hashpw(target_password.encode('utf-8'), bcrypt.gensalt(rounds=12))

print("=== Результати хешування ===")
print(f"Хеш №5 (SHA-256): {hash_sha256}")
print(f"Хеш №6 (bcrypt):  {hash_bcrypt.decode('utf-8')}\n")

# 13. Атака перебором для SHA-256
start_sha = time.time()
for candidate in dictionary:
    cand_hash = hashlib.sha256(candidate.encode('utf-8')).hexdigest()
    if cand_hash == hash_sha256:
        break
time_sha = time.time() - start_sha
print(f"[SHA-256] Знайдено! Час виконання: {time_sha:.6f} сек")

# 13. Атака перебором для bcrypt
start_bcrypt = time.time()
for candidate in dictionary:
    if bcrypt.checkpw(candidate.encode('utf-8'), hash_bcrypt):
        break
time_bcrypt = time.time() - start_bcrypt
print(f"[bcrypt]   Знайдено! Час виконання: {time_bcrypt:.6f} сек")
