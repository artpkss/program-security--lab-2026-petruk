import bcrypt

users_db = {}

def register(email, password):
    if email in users_db:
        return False, "Користувач вже існує"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
    users_db[email] = {"password_hash": hashed, "role": "user"}
    return True, "Успішна реєстрація"

def login(email, password):
    user = users_db.get(email)
    if not user:
        return False, "Невірна електронна пошта або пароль"
    if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        return True, f"Успішний вхід! Вітаємо, {email}."
    return False, "Невірна електронна пошта або пароль"

if __name__ == "__main__":
    print("=== ТЕСТУВАННЯ СИСТЕМИ АВТЕНТИФІКАЦІЇ ===")
    status, msg = register("petruka@khmnu.edu.ua", "pass: petruk")
    print(f"Реєстрація: {msg}")
    
    status, msg = login("petruka@khmnu.edu.ua", "wrong_pass")
    print(f"Вхід із невірним паролем: {msg}")
    
    status, msg = login("petruka@khmnu.edu.ua", "pass: petruk")
    print(f"Вхід із правильним паролем: {msg}")
