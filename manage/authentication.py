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

from pathlib import Path

from admin import admin
from developer import developer

class authentication():
    def __init__(self, username, password):
        self.authenticate(username, password)

    def start_client(self):
        if self.client_type == "admin":
            return admin()
        elif self.client_type == "dev":
            return developer()

    def authenticate(self, username, password):
        self._read_password_file()

        reason = ""
        username_result, password_result = False, False
        if username in self._users: 
            username_result = True
            if self._users[username][0] == password:
                password_result = True
            else:
                reason = "Wrong password"
        else:
            reason = "User not found"

        self.result = username_result and password_result 
        self.client_type = self._users[username][1]
        if self.result:
            print("Access Granted")
        else:
            print(f"Access Denied - {reason}")
        
        

    def _read_password_file(self):
        self._users = {}
        password_file = Path(__file__).resolve().parent / "data/passwords.ini"
        try:
            print(f"Reading user database from {password_file}")
            with open(password_file, "r") as fout:
                lines = fout.readlines()
                for line in lines:
                    if line[0] == "#" or line[0] == "\n" or line[0] == " ":
                        pass
                    else:
                        line = [i.strip() for i in line.strip("\n").split(":")]
                        self._users[line[0]] = [line[1], line[2]]
                
            print(f"{len(self._users)} user(s) read from file {password_file}")
        except FileNotFoundError:
            print(f"Password file {password_file} not found")

if __name__ == "__main__":
    auth = authentication("admin", "adminPassword123")
    c = auth.start_client()
    print(c.products)