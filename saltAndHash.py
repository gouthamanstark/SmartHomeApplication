import bcrypt

# Used for adding salt and hashing the user password
def hashPassword(password):
    hashedPassword=bcrypt.hashpw(password.encode(),bcrypt.gensalt())
    return hashedPassword

# Used to verify the input password by comparing it with the respective user's hash
def verifyPassword(password,hash):
    result=bcrypt.checkpw(password.encode(),hash.encode())
    return result
