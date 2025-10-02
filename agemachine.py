"""This function takes the integer age as input and prints if the person is old or young."""

def ageMachine(age: int)-> None:
    if age > 50:
        print ("You are old")
    else:
        print ("You are still young")

print("How old are you?")

age_from_user = input()
age_from_user = int(age_from_user)  

ageMachine(age_from_user)