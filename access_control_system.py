import bcrypt

# База даних користувачів
users_db = {
    "user@khmnu.edu.ua": {
        "password_hash": bcrypt.hashpw(b"user123", bcrypt.gensalt(10)),
        "role": "user",
        "id": 101
    },
    "admin@khmnu.edu.ua": {
        "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt(10)),
        "role": "admin",
        "id": 1
    }
}

# Поточний автентифікований користувач (сесія)
current_user = None

def login(email, password):
    global current_user
    user = users_db.get(email)
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        current_user = {"email": email, "role": user["role"], "id": user["id"]}
        print(f"\n[AUTH] Успішний вхід: {email} (Роль: {user['role']})")
        return True
    print(f"\n[AUTH] Помилка входу для {email}")
    return False

def logout():
    global current_user
    print(f"[AUTH] Вихід із системи ({current_user['email'] if current_user else 'Гість'}).")
    current_user = None

# Функція перевірки доступу (RBAC + DAC)
def check_permission(required_role=None, allow_owner_id=None):
    if not current_user:
        print("   ❌ [401 Unauthorized] Відмова: Ви не увійшли в систему!")
        return False
    
    # 1. Адміністратор має повні права (RBAC)
    if current_user["role"] == "admin":
        return True
    
    # 2. Власник ресурсу має право на редагування (DAC)
    if allow_owner_id is not None and current_user["id"] == allow_owner_id:
        return True
    
    # 3. Перевірка відповідності ролі (RBAC)
    if required_role and current_user["role"] == required_role:
        return True
        
    print(f"   ❌ [403 Forbidden] Відмова для {current_user['email']}! Недостатньо прав.")
    return False

# Захищені функції
def view_dashboard():
    print("--- Спроба доступу: Адмін-панель ---")
    if check_permission(required_role="admin"):
        print("   ✅ [200 OK] Успішний доступ до System Dashboard")

def edit_profile(profile_owner_id):
    print(f"--- Спроба доступу: Редагування профілю ID={profile_owner_id} ---")
    if check_permission(allow_owner_id=profile_owner_id):
        print(f"   ✅ [200 OK] Профіль ID={profile_owner_id} успішно змінено!")

# Тестування (Пункт 9)
if __name__ == "__main__":
    print("================ ТЕСТУВАННЯ МОДЕЛІ ДОСТУПУ ================")

    print("\n1. Сценарій: Спроба дій без авторизації (Гість):")
    view_dashboard()
    edit_profile(101)

    print("\n2. Сценарій: Дії звичайного користувача (User):")
    login("user@khmnu.edu.ua", "user123")
    edit_profile(101)  # Свій профіль (Дозволено)
    edit_profile(1)    # Чужий профіль (Заборонено)
    view_dashboard()   # Адмін-панель (Заборонено)
    logout()

    print("\n3. Сценарій: Дії адміністратора (Admin):")
    login("admin@khmnu.edu.ua", "admin123")
    view_dashboard()   # Дозволено
    edit_profile(101)  # Чужий профіль (Дозволено для Admin)
    logout()
