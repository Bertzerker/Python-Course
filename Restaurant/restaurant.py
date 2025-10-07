# -*- coding: utf-8 -*-
"""
Simulierter Restaurant-Dialog (Kommandozeile)
Einfacher Ablauf: Kunde bestellt -> Kellner -> Küche -> Essen serviert
"""

import time

MENU_ITEMS = {
    "1": "Pizza", "01": "Pizza", "pizza": "Pizza",
    "2": "Pasta", "02": "Pasta", "pasta": "Pasta",
    "3": "Bruschetta", "03": "Bruschetta", "bruschetta": "Bruschetta",
    "4": "Steak", "04": "Steak", "steak": "Steak",
}

# Für Erkennung von Namen in ganzen Sätzen
ITEM_NAMES = ["pizza", "pasta", "bruschetta", "steak"]

def parse_choice(raw: str):
    s = raw.strip().lower()
    if not s:
        return None

    # Direkter exakter Treffer (z. B. "01" oder "pizza")
    if s in MENU_ITEMS:
        return MENU_ITEMS[s]

    # Falls ein Menü-Name irgendwo im Satz vorkommt
    for name in ITEM_NAMES:
        if name in s:  # z. B. "pizza" in "ich hätte gerne die pizza"
            return MENU_ITEMS[name]

    # Ziffern extrahieren (für Fälle wie "Ich nehme die 03 bitte")
    digits = "".join(ch for ch in s if ch.isdigit())
    if digits:
        d2 = digits[:2]  # auf max. 2 Stellen kürzen
        for key in (d2, d2.lstrip("0")):
            if key in MENU_ITEMS:
                return MENU_ITEMS[key]

    return None

def ask_menu() -> str:
    while True:
        print("\nMenükarte:")
        print("  01. Pizza")
        print("  02. Pasta")
        print("  03. Bruschetta")
        print("  04. Steak")
        choice = input("Was möchten Sie bestellen? (ganzer Satz, Nummer oder Name, 'q' zum Abbrechen): ").strip()
        if choice.lower() in {"q", "quit"}:
            raise KeyboardInterrupt("Bestellung abgebrochen.")
        item = parse_choice(choice)
        if item:
            return item
        print("→ Ungültige Eingabe, bitte erneut versuchen!")

def main():
    # 01–03 Kunde ruft Kellner
    print("Bedienung bitte!")
    time.sleep(0.5)

    # 04 Kellner geht zum Tisch
    print("Kellner geht zum Tisch...")
    time.sleep(0.5)

    # 05–07 Bestellung
    print("Kellner: Sie möchten bestellen?")
    try:
        order = ask_menu()
    except KeyboardInterrupt:
        print("Kellner: Alles klar, ich komme später nochmal vorbei.")
        print("Programm beendet.")
        return

    print(f"Kunde: Ich hätte gerne {order}!")

    # 08–10 Kellner notiert und bestätigt
    print(f"Kellner: Einmal {order}, kommt sofort!")
    time.sleep(0.5)

    # 11–12 Kellner übergibt an Küche
    print(f"Kellner (zur Küche): Einmal {order} bitte!")
    time.sleep(1)

    # 13 Küche kocht
    print(f"Küche bereitet {order} zu...")
    time.sleep(2)

    # 14–15 Kellner liefert Essen
    print(f"Kellner: Einmal {order} für Sie, guten Appetit!")

    # 16 Ende
    print("Programm beendet.")

if __name__ == "__main__":
    main()
