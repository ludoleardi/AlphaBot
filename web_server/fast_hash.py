import hashlib

hash_object = hashlib.sha256(input("Inserisci stringa da hashare: ").encode())
hashed_string = hash_object.hexdigest()
print(hashed_string)