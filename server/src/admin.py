# Author: Liu Yanzhao
# Admin No / Grp: 240333N / AA2402
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

# importing neccessary libraries
import json
from pathlib import Path

# custom exceptions
class productNotFoundError(Exception):
    pass

class itemNotFoundError(Exception):
    pass

class invalidValueError(Exception):
    def __init__(self, message):
        """
        custom invalid value error

        :param message: error message
        """
        self.message = message

# admin class
class admin():
    def __init__(self) -> None:
        """
        initiliaise admin class

        retrieve product from products.json
        """
        print("Starting as admin")
        self.retrieve_products()
        

    def retrieve_products(self):
        """
        open products.json file and load the json inside into self.products
        retrieve keys and append them into self.products_key
        """
        f = open(Path(__file__).resolve().parent / "data/products.json", "r")
        self.products = json.load(f)
        f.close()
        self.products_key = []
        for key in self.products:
            self.products_key.append(key)

    def update_products(self):
        """
        update_product saves the current product json 
        in primary storage into json file in secondary storage
        """
        f = open(Path(__file__).resolve().parent / "data/products.json", "w")
        string_products = json.dumps(self.products)
        f.write(string_products)
        f.close()

    def new_product(self, product_id, product_name, category, description, price, quantity_available):
        """
        add new product

        :param product_id: product id to be added
        :param product_name: product name to be added
        :param category: category to be added to
        :param description: description of product to be added
        :param price: price of product to be added
        :param quantity_available: quantity of product to be added
        """
        try:
            print(product_id)
            if product_id == "":
                raise invalidValueError("Product ID cannot be blank")
            if product_name == "":
                raise invalidValueError("Product Name cannot be blank")
            if product_id in self.products_key:
                raise invalidValueError("provided new product ID is not unique")
            if not category in ["Electronics", "Mobile Devices", "Accessories", "Home Appliance", "Accessories"]:
                raise invalidValueError("Provided new product category is invalid")
            if not self.is_float(str(price)):
                raise invalidValueError("Price is not a positive float")
            if not str(quantity_available).isnumeric():
                raise invalidValueError("Quanitity Available is not a positive whole number")
            
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
        """
        check if the string is a float

        :param string: string tot check if it a float 
        """
        one_decimal_point = string.count('.') <= 1
        string_is_numeric = string.replace(".", "").isnumeric()
        return one_decimal_point and string_is_numeric

    def change_product(self, product_id, new):
        """
        change product

        :param product_id: product_id that is to be changed
        :param new: new dictionary of product to be changed
        """
        try:
            # Error
            if product_id == "":
                raise invalidValueError("Product ID cannot be blank")
            if not product_id in self.products:
                raise productNotFoundError
            if len(new) != 5: 
                raise itemNotFoundError
            for i in ["Product Name", "Category", "Description", "Price", "Quantity Available"]:
                if i not in new:
                    raise itemNotFoundError
            if new["Product Name"] == "":
                raise invalidValueError("Product Name cannot be blank")
            if not new["Category"] in ["Electronics", "Mobile Devices", "Accessories", "Home Appliance", "Accessories"]:
                raise invalidValueError("provided new product category is invalid")
            if not self.is_float(new["Price"]):
                raise invalidValueError("Price is not a positive float")
            if not new["Quantity Available"].isnumeric():
                raise invalidValueError("Quanitity Available is not a positive whole number")
    
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
        """
        product can be removed entirely

        :param product: the product id of the product
        """
        try:
            if not product in self.products:
                raise productNotFoundError
            
            removed_item = self.products.pop(product)
            print(f"{removed_item} is removed")
            self.update_products()

        except productNotFoundError:
            print("product not found")

# testing
if __name__ == "__main__":
    c = admin()
    c.new_product("5001", "Blender", "Home Appliance", "spinny blade so cool!", 100, 100)
    c.change_product("1001", {
        "Product Name": "smt new",
        "Category": "Electronics",
        "Description": "High-performance laptop with SSD storage",
        "Price": "1288.88",
        "Quantity Available": "50"
    })