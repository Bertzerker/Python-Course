# Definition von Variablen für Namen, Alter und Höhe
name1, alter1, hoehe1 = "Anna", 25, 1.68
name2, alter2, hoehe2 = "Ben", 32, 1.82
name3, alter3, hoehe3 = "Clara", 28, 1.75

print(name1, alter1, hoehe1)
print(name2, alter2, hoehe2)
print(name3, alter3, hoehe3)



# Berechnung der Fläche eines Rechtecks
laenge = 5.4
breite = 3.2

flaeche = laenge * breite

print("Die Fläche des Rechtecks beträgt:", flaeche)



# Definition von Variablen mit verschiedenen Datentypen
alter = 25             # int-Wert
temperatur = 18.6      # float-Wert
haustier_name = "Bello"  # string-Wert
regnet = True           # bool-Wert

print("Alter:", alter)
print("Temperatur:", temperatur, "°C")
print("Name des Haustiers:", haustier_name)
print("Regnet es draußen?", regnet)



# Addition von zwei int-Zahlen
zahl1 = 7
zahl2 = 5
summe = zahl1 + zahl2

# Fläche eines Kreises (Formel: π * r²)
import math
radius = 3.5
flaeche = math.pi * radius ** 2

# Zwei Strings kombinieren
text1 = "Hallo"
text2 = "Welt!"
nachricht = text1 + " " + text2

print("Ergebnis der Addition:", summe)
print("Fläche des Kreises:", flaeche)
print("Kombinierte Nachricht:", nachricht)



# Benutzereingaben speichern und ausgeben
name = input("Wie heißt du? ")
alter = input("Wie alt bist du? ")
lieblingsessen = input("Was ist dein Lieblingsessen? ")

print(f"Hallo {name}, du bist {alter} Jahre alt und dein Lieblingsessen ist {lieblingsessen}.")