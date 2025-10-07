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

def parse_choice(raw: str):
    s = raw.strip().lower()
    if s in MENU_ITEMS:
        return MENU_ITEMS[s]
    digits = "".join(ch for ch in s if ch.isdigit())
    return MENU_ITEMS.get(digits)

def ask_menu() -> str:
    while True:
        print("\nMenükarte: [Zahlen werden nach der 2. Stelle abgeschnitten]")
        print("  01. Pizza")
        print("  02. Pasta")
        print("  03. Bruschetta")
        print("  04. Steak")
        choice = input("Was möchten Sie bestellen? (Nummer oder Name eingeben): ")
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
    order = ask_menu()
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
