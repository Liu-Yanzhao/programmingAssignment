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

class invalidValueError(Exception):
    def __init__(self, message):
        self.message = message

class admin():
    def __init__(self) -> None:
        print("Starting as admin")
        self.retrieve_products()
        self.products_key = []
        for key in self.products:
            self.products_key.append(key)

    def retrieve_products(self):
        f = open(Path(__file__).resolve().parent / "data/products.json", "r")
        self.products = json.load(f)
        f.close()

    def update_products(self):
        '''
        update_product saves the current product json 
        in primary storage into json file in secondary storage
        '''
        f = open(Path(__file__).resolve().parent / "data/products.json", "w")
        string_products = json.dumps(self.products)
        f.write(string_products)
        f.close()

    def new_product(self, product_id, product_name, category, description, price, quantity_available):
        try:
            if product_id in self.products_key:
                raise invalidValueError("provided new product ID is not unique")
            if not category in ["Electronics", "Mobile Devices", "Accessories", "Home Appliance", "Accessories"]:
                raise invalidValueError("provided new product category is invalid")
            if not self.is_float(str(price)):
                raise invalidValueError("price is not a float")
            if not str(quantity_available).isnumeric():
                raise invalidValueError("Quanitity Available is not a whole number")
            
            self.products[product_id] = {
                "Product Name": product_name,
                "Category": category,
                "Description": description,
                "Price": price,
                "Quantity Available": quantity_available
            }
            self.update_products()
            return "None"
        except productNotFoundError:
            return "product not found"
        except itemNotFoundError:
            return "item not found"
        except invalidValueError as e:
            return e.message
        except Exception as e:
            return e

    def is_float(self, string):
        one_decimal_point = string.count('.') <= 1
        string_is_numeric = string.replace(".", "").isnumeric()
        return one_decimal_point and string_is_numeric

    def change_product(self, product_id, new):
        ''' 
        product is product id of the proudct
        item can be: "Product ID", "Product Name", "Category", "Description", "Price", "Quantity Available"
        new is the new value to update product
        '''
        try:
            # Error
            if not product_id in self.products:
                raise productNotFoundError
            if len(new) != 5: 
                raise itemNotFoundError
            for i in ["Product Name", "Category", "Description", "Price", "Quantity Available"]:
                if i not in new:
                    raise itemNotFoundError
            if not new["Category"] in ["Electronics", "Mobile Devices", "Accessories", "Home Appliance", "Accessories"]:
                raise invalidValueError("provided new product category is invalid")
            if not self.is_float(new["Price"]):
                raise invalidValueError("price is not a float")
            if not new["Quantity Available"].isnumeric():
                raise invalidValueError("Quanitity Available is not a whole number")
    
            new["Price"] = float(new["Price"])
            new["Quantity Available"] = int(new["Quantity Available"])

            self.products[product_id] = new
            self.update_products()
            return "None"

        except productNotFoundError:
            return "product not found"
        except itemNotFoundError:
            return "item not found"
        except invalidValueError as e:
            return e.message
        except Exception as e:
            return e

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
    # testing
    c = admin()
    c.new_product("5001", "Blender", "Home Appliance", "spinny blade so cool!", 100, 100)
    c.change_product("1001", {
        "Product Name": "smt new",
        "Category": "Electronics",
        "Description": "High-performance laptop with SSD storage",
        "Price": "1288.88",
        "Quantity Available": "50"
    })