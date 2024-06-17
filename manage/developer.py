# Copyright (c) 2024 yamgao_

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from cryptography.fernet import Fernet
from pathlib import Path

class invalidNewChange(Exception):
    def __init__(self, message):
        self.message = message

class developer():
    def __init__(self) -> None:
        print("Starting as developer")
        self._read_password_file()

    def _read_password_file(self):
        self._users = {}
        password_file = Path(__file__).resolve().parent / "data/passwords.ini"
        key_file = Path(__file__).resolve().parent / "data/fernet.key"

        try:
            print(f"Reading user database from {key_file}")
            key = ""
            with open(key_file, "r") as fout:
                lines = fout.readlines()
                for line in lines:
                    if line[0] == "#" or line[0] == "\n" or line[0] == " ":
                        pass
                    elif line.strip("\n") == "-----BEGIN FERNET KEY-----":
                        pass
                    elif line.strip("\n") == "-----BEGIN FERNET KEY-----":
                        break
                    else:
                        key += line.strip("\n")
            print(f"key is read from file {password_file}")
        except FileNotFoundError:
            print(f"key file {key_file} not found")

        self.fernet = Fernet(key.encode())

        try:
            print(f"Reading user database from {password_file}")
            with open(password_file, "r") as fout:
                lines = fout.readlines()
                for line in lines:
                    if line[0] == "#" or line[0] == "\n" or line[0] == " ":
                        pass
                    else:
                        line = [i.strip() for i in line.strip("\n").split(":")]
                        self._users[line[0]] = [self.fernet.decrypt(line[1].encode()).decode(), line[2]]
                
            print(f"{len(self._users)} user(s) read from file {password_file}")
        except FileNotFoundError:
            print(f"Password file {password_file} not found")
    
    def update_file(self, file, new):
        f = open(Path(__file__).resolve().parent / file, "w")
        f.write(new)
        f.close()

    def change_key(self):
        new_key = Fernet.generate_key() # generate new key
        self.fernet = Fernet(new_key)
        new_key = f"-----BEGIN FERNET KEY-----\n{str(new_key)[2:-1]}\n-----BEGIN FERNET KEY-----"
        self.update_file("data/fernet.key", new_key)
        
        password = "# you can add access control here as username:passwords:client_type.\n\n"
        for i in self._users:
            password += f"{i}:{str(self.fernet.encrypt(self._users[i][0].encode()))[2:-1]}:{self._users[i][1]}\n"
        self.update_file("data/passwords.ini", password)

    def change_access_control(self, username, change_type, new):
        if not change_type in ["username", "password", "client type"]:
            raise invalidNewChange("Can only be 'username', 'password' or 'client type'")
        if change_type == "client type" and not new in ["admin", "dev"]:
            raise invalidNewChange("can only be 'admin' or 'dev'")
        if not username in self._users:
            raise invalidNewChange("username not found")
        
        if change_type == "username":
            oldPasswordClientType = self._users[username]
            self._users.pop(username)
            self._users.update(new, oldPasswordClientType)
        elif change_type == "password":
            self._users[username][0] = new
        elif change_type == "client type":
            self._users[username][1] = new

        password = "# you can add access control here as username:passwords:client_type.\n\n"
        for i in self._users:
            password += f"{i}:{str(self.fernet.encrypt(self._users[i][0].encode()))[2:-1]}:{self._users[i][1]}\n"
        self.update_file("data/passwords.ini", password)

if __name__ == "__main__":
    c = developer()
    c.change_key()
    c.change_access_control("admin", "password", "test")
    c.change_access_control("admin", "client type", "admin")
    c.change_access_control("admin", "username", "test")