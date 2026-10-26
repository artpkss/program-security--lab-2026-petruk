tasks_db = {
    "user1": {"name": "Костя", "tasks": ["Прибирання", "Купити продукти"]},
    "user2": {"name": "Артем", "tasks": ["Здати ЛР №5", "Завантажити звіт на GitHub"]}
}

def show_user_menu(user_id):
    user = tasks_db.get(user_id)
    if not user:
        print("❌ Користувача не знайдено")
        return
    print(f"\n==========================================")
    print(f" Меню користувача: {user['name']} ({user_id})")
    print(f"==========================================")
    print(" [ОБ'ЄКТИ ДОСТУПУ (DAC/RBAC)]")
    for idx, task in enumerate(user['tasks'], 1):
        print(f"  {idx}. {task}")
    print("------------------------------------------")

if __name__ == "__main__":
    show_user_menu("user1")
    show_user_menu("user2")
