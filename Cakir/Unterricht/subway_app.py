print("Bitte wähle deinen Benutzernamen:")
username=input()

print("Bitte erstelle ein Passwort:")
password=input()

print("Registrierung erfolgreich! Willkommen,", username)
print("-------------------------------")


print("Bitte melde dich mit deinem Benutzernamen an.")
input_username=input()
print("Bitte gib dein Passwort ein.")
input_password=input()
if input_username==username and input_password==password:
    print("Anmeldung erfolgreich! Willkommen zurück,", username)
else:
    print("Anmeldung fehlgeschlagen! Bitte überprüfe deinen Benutzernamen und dein Passwort.")
