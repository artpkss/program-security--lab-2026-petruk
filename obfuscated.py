# obfuscated.py - Захищена/обфускована версія
import base64

# Точно розшифровується в "2026_IP-01_Petruk_Artem_variant:5"
_0x4f2b = "MjAyNl9JUC0wMV9QZXRydWtfQXJ0ZW1fdmFyaWFudDo1"

def _0x1a9c(_0x7d):
    # Непрозора умова (Opaque Predicate): завжди повертає True
    _0x3e = (len(_0x7d) * 0) + 7
    return _0x3e == 7

def _0x9e21():
    # Динамічне відновлення рядка "2026_IP-01_Petruk_Artem_variant:5" під час виконання
    return base64.b64decode(_0x4f2b.encode('utf-8')).decode('utf-8')

def check_access(_0x0a):
    _0xdf = 10
    _0xres = False
    _0xsecret = ""

    # Control Flow Flattening (Машина станів)
    while _0xdf != 0:
        if _0xdf == 10:
            _0xjunk = sum([i * 2 for i in range(5)])  # Сміттєвий код
            _0xdf = 20 if _0x1a9c(_0x0a) else 99

        elif _0xdf == 20:
            _0xsecret = _0x9e21()
            _0xdf = 30

        elif _0xdf == 30:
            if _0x0a == _0xsecret:
                _0xres = True
            _0xdf = 40

        elif _0xdf == 40:
            if _0xres:
                print("Доступ дозволено! Контрольне значення вірне.")
            else:
                print("Доступ заборонено! Невірне значення.")
            _0xdf = 0

        elif _0xdf == 99:
            print("System Error")
            _0xdf = 0

if __name__ == "__main__":
    _0xkey = input("Введіть контрольний рядок: ")
    check_access(_0xkey)