a="7"
b="5"

print(a+b)  # Ausgabe: 75
print(int(a)+int(b))  # Ausgabe: 12

c="3.5"
d="2.9"
ergebnis=float(c)/float(d)

print(float(c)/float(d)) 
print(f"Das Ergebnis der Division ist: {ergebnis:.2f}")  # Ausgabe mit 2 Dezimalstellen

studenten1= ["Anna", "Bert", "Cem", "Dora"] # Liste von Studenten
print(studenten1)
print(", ".join(studenten1))  # Ausgabe der Liste als kommagetrennte Zeichenkette
print("g ".join(studenten1))  # Ausgabe der Liste als durch 'g' getrennte Zeichenkette

studenten2= ["Anna", "Bert", "Cem", "Dora"] # Liste von Studenten
ausgabe= ", ".join(studenten2)
print(f"Das sind meine liebsten Studenten {ausgabe}.")  # Ausgabe mit f-String

studenten3= "Anna,Bert,Cem,Dora" # Liste von Studenten
ergebnis=(studenten3.split(","))  # Aufteilen der Zeichenkette in eine Liste anhand des Kommas
print(ergebnis)
print(type(studenten3))
print(type(ergebnis))

test=["test","zweite stelle","dritte stelle"]
print(test[2])  # Ausgabe: dritte stelle

tier= "Wer hat die Gans gestohlen?"
print(tier.split(" "))  # Aufteilen der Zeichenkette in eine Liste anhand des Leerzeichens  

# oder und Schaltungen
Salat= True
mitFleisch= False
mitBrot= True
mitKäse= True

doener= Salat and (mitFleisch or (mitBrot and mitKäse))
print(doener)