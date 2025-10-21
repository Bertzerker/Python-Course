'''Aufgabe: Erstelle ein Programm, das den Energieverbrauch eines Haushalts berechnet. Definiere logische Funktionen,
 um den Verbrauch basierend auf verschiedenen Geräten und deren Nutzungsdauer zu ermitteln.

Informationen:
In jedem Haushalt gibt es 3 Fernseher a 1 kWh und es wird täglich 3 Stunden Game of Thrones geschaut.
Der Herd verbraucht 2 kWh pro Stunde und wird 4 mal die Woche für 2 Stunden genutzt.
Telefon und Router sowie Rechner verbrauchen 2kWh und sind insgesamt 4 Stunden am Tag in Betrieb.
Ein Familienmitglied ist sparsam und benutzt eine elektrische Heizung mit 8kWh an 170 Tagen im Jahr für 20 Stunden.

Berechne den Verbrauch und Stromkosten, wenn 1 kWh 0,40 Euro kostet.'''

strompreis= 0.40

verbrauch_tv= 3*1*3*365
verbrauch_herd= 4*2*2*52
verbrauch_router= 2*4*365
verbrauch_heizung= 8*20*170

gesamtverbrauch= verbrauch_tv + verbrauch_herd + verbrauch_router + verbrauch_heizung
                #0.40 Euro pro kWh
gesamtkosten= gesamtverbrauch * strompreis

print(f"Die Gesamtkosten sind: {gesamtkosten:.2f} Euro") # empfohlene Formatierung
print("Die Gesamtkosten sind: ", gesamtkosten, " Euro")
