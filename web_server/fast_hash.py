import hashlib

#Programma utilizzato esclusivamente per calcolare i digest delle password da inserire nel DB
hash_object = hashlib.sha256(input("Inserisci stringa da hashare: ").encode())
hashed_string = hash_object.hexdigest()
print(hashed_string)