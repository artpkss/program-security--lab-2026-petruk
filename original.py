# original.py - Базова версія без захисту

SECRET_KEY = "2026_IP-01_Petruk_Artem_variant:5"

def check_access(user_input):
    if user_input == SECRET_KEY:
        print("Доступ дозволено! Контрольне значення вірне.")
    else:
        print("Доступ заборонено! Невірне значення.")

if __name__ == "__main__":
    key = input("Введіть контрольний рядок: ")
    check_access(key)