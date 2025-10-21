# implementation Cesar Encryption

ALPHABET = [
    ' ','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]
ALPHABET_LEN = len(ALPHABET)

#this function ask user for key encryption and return int 
def getKey()->int:
    #because allways what user typed in cli will be saved as string!
    key = input("please enter encryption Key:")
    #we mus change the type to integer ! 
    key = int(key)
    return key


#this function do encryption
def encrypt()->str:
    result = ""
    #klar_text is what user typed for example jojo
    klarText = input("\nplease enter Text to be encrypted:")
    key = getKey()
    for character in klarText:
        #we find position of each character in our ALPHABET ARRAY! 
        #when charechter == j => alphabet_index == 10
        alphabet_index = ALPHABET.index(character)
        encryptedChar_index = (alphabet_index+key) % ALPHABET_LEN
        #result = result + ALPHABET[encryptedChar_index]
        result += ALPHABET[encryptedChar_index]
    return result

def decode()->str:
    result = ""
    cypherText = input("\nplease enter Text to be DECRYPTED!!:")
    key = getKey()
    for character in cypherText:
        #we find position of each character in our ALPHABET ARRAY! 
        #when character == j => alphabet_index == 10
        alphabet_index = ALPHABET.index(character)
        encryptedChar_index = (alphabet_index-key) % ALPHABET_LEN
        #result = result + ALPHABET[encryptedChar_index]
        result += ALPHABET[encryptedChar_index]
    return result

def main():
    result =""
    print("hello , i am cesar enc and dec app!")
    userChoice = input("if you want decrypt press d oder encrypt press e:")

    if(userChoice == "e"):
        result = encrypt()
    elif userChoice == "d":
        result = decode()
    else:
        result = "you must enter only e or d"

    print(result)

if __name__ == "__main__":
    main()