# password_manager.py
# by Preston Hager

import bcrypt

from os import environ

class PasswordManager:
    def __init__(self, default_salt=",_5$nS92,N%HAO-WRxIuV9J53mv|`gUBfC:({$rIWF)>0{S']|MhoLE^\":M,*$I"):
        self.salt = environ.get("PASS_SALT")
        if self.salt == None:
            self.salt = default_salt

    def hash_password(self, password):
        return bcrypt.hashpw(self.salt + password, bcrypt.gensalt())

    def compare(self, password, hash):
        return bcrypt.checkpw(self.salt + password, hash)

class AuthorizationManager:
    def __init__(self, database):
        self.database = database

    def generate_authorization(self, username):
        key_item = self.database.new_access_key(username)
        del key_item['username']
        return key_item

    def check(self, access_key):
        key = self.database.get_access_key(access_key)
        if key == None:
            return False
        return True

__all__ = ["PasswordManager", "AuthorizationManager"]
