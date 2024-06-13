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
import json

class productNotFoundError(Exception):
    pass

class itemNotFoundError(Exception):
    pass

class invalidNewValueError(Exception):
    def __init__(self, message):
        self.message = message

class admin():
    def __init__(self, username, password) -> None:
        result = self.authentication(username, password)
        if result:
            self.main()
        

    def authentication(self, username, password):
        self._read_password_file()

        reason = ""
        username_result, password_result = False, False
        if username in self._users: 
            username_result = True
            if self._users[username] == password:
                password_result = True
            else:
                reason = "Wrong password"
        else:
            reason = "User not found"

        result = username_result and password_result
        if result:
            print("Access Granted")
            self.main()
        else:
            print(f"Access Denied - {reason}")
        return result

    def _read_password_file(self):
        self._users = {}
        password_file = Path(__file__).resolve().parent / "database/passwords.ini"
        try:
            print(f"Reading user database from {password_file}")
            with open(password_file, "r") as fout:
                lines = fout.readlines()
                for line in lines:
                    if line[0] == "#" or line[0] == "\n" or line[0] == " ":
                        pass
                    else:
                        line = [i.strip() for i in line.strip("\n").split(":")]
                        self._users[line[0]] = line[1]
                
            print(f"{len(self._users)} user(s) read from file {password_file}")
        except FileNotFoundError:
            print(f"Password file {password_file} not found")

    def main(self):
        self.retrieve_products()

    def retrieve_products(self):
        f = open(Path(__file__).resolve().parent / "database/products.json")
        self.products = json.load(f)
        f.close()
        print(self.products)
        self.products_key = []
        for key in self.products:
            self.products_key.append(key)
        

    def update_products(self):
        '''
        update_product saves the current product json 
        in primary storage into json file in secondary storage
        '''
        f = open(Path(__file__).resolve().parent / "database/products.json")
        string_products = str(self.products)
        f.write(string_products)

    def new_product(self):
        pass

    def is_float(self, string):
        one_decimal_point = string.count('.') <= 1
        string_is_numeric = string.replace(".", "").isnumeric()
        return one_decimal_point and string_is_numeric


    def change_product(self, product, item, new):
        ''' 
        product is product id of the proudct
        item can be: "Product ID", "Product Name", "Category", "Description", "Price", "Quantity Available"
        new is the new value to update product
        '''
        try:
            if not product in self.products:
                raise productNotFoundError
            if not item in ["Product ID", "Product Name", "Category", "Description", "Price", "Quantity Available"]:
                raise itemNotFoundError

            if item == "Product ID" and new in self.products_key:
                raise invalidNewValueError("provided new product ID is not unique")
            if item == "Product ID" and new in ["Electronics", "Mobile Devices", "Accessories", "Home Appliance", "Accessories"]:
                raise invalidNewValueError("provided new product category is invalid")
            if item == "Price" and not self.is_float(new):
                raise invalidNewValueError("price is not a float")
            if item == "Quantity Available" and not new.isnumeric():
                raise invalidNewValueError("Quanitity Available is not a whole number")

            self.products[product][item] = new
            self.update_products()

        except productNotFoundError:
            print("product not found")
        except itemNotFoundError:
            print("item not found")
        except invalidNewValueError as e:
            print(e.message)
        except Exception as e:
            print(e)
    

    def remove_product(self, product):
        '''
        product can be removed entirely
        product is the product id of the product
        '''
        try:
            if not product in self.products:
                raise productNotFoundError
            
            removed_item = self.products.pop(product)
            print(f"{removed_item} is removed")
            self.update_products()

        except productNotFoundError:
            print("product not found")

if __name__ == "__main__":
    c = admin("client", "iLoveMrChan")
    c.change_product("1001", "Quantity Available", "2001")

