import bcrypt
import os
import psycopg2

def create_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Example usage:
password = "Admin@123"
hashed_password = create_password(password)
print(hashed_password)
