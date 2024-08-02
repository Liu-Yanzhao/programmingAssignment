# Importing required libraries
import cv2 # OpenCV for image and video processing
import json # JSON library for parsing JSON data
import random # Random library for generating random numbers
import logging # logging libraries for logging messages
import asyncio # Asyncio library for asynchronous programming

# Importing user-defined libraries
from src.scanner import scanner

# Importing server-side libraries for MQTT communication
from amqtt.mqtt.constants import QOS_1
from amqtt.codecs import int_to_bytes_str
from amqtt.client import MQTTClient, ClientException

# Importing Kivy libraries for UI devlopment
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.uix.image import Image
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition 

# Importing Kivy Builder library for UI support
from kivy.lang import Builder
from kivy.core.window import Window


# Server IP address
SERVER_IP = "127.0.0.1" # for testing purpose, the server ip is localhost

# Kivy string for UI layout
kv_string = """
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout: 
            padding: 100
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Username:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300
            TextInput:
                id: username
                multiline: False
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50

        BoxLayout:
            padding: 100
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Password:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300

            TextInput:
                id: password
                password: True
                multiline: False
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50

        BoxLayout:
            padding: 100
            Button:
                background_color: 
                text: 'Login'
                on_press:  root.run_login(username.text, password.text)

<AdminScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            MDIconButton:
                icon: "plus"
                style: "standard"
                on_press: root.add()
            MDIconButton:
                icon: "database-search-outline"
                style: "standard"
                on_press: root.search(search.text)
            TextInput:
                id: search
                multiline: False
                cursor_color: (0,0,0,1)
                height: 50
                size_hint: {0.5, None}
                pos_hint: {"x":500}
                pos_hint: {'center_y': 0.25, 'center_x': 0.5}
            MDIconButton:
                icon: "refresh"
                style: "standard"
                on_press: root.reload() 
            MDIconButton:
                icon: "barcode-scan"
                style: "standard"
                on_press: root.scan()

        BoxLayout:
            pos_hint: {'center_y': 0.5, 'center_x': 0.5}
            size_hint: (0.5, 4)
        BoxLayout:
            Label:
                text: 'Admin Dashboard'
                color: 0,0,0,1
                size_hint: (.2, None)

            MDIconButton:
                icon: "exit-to-app"
                style: "standard"
                on_press: app.root.current = "loginScreen"


<ProductScreen>
    BoxLayout:
        orientation: 'vertical'
        BoxLayout: 
            size_hint: (0.95, 0.1)
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Product ID:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300
            TextInput:
                id: product_id
                multiline: False
                readonly: True
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50

        BoxLayout:
            size_hint: (0.95, 0.1)
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Product Name:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300
            TextInput:
                id: product_name
                multiline: False
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50
        
        BoxLayout:
            size_hint: (0.95, 0.1)
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Category:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300
            TextInput:
                id: category
                multiline: False
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50

        BoxLayout:
            size_hint: (0.95, 0.1)
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Price:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300
            TextInput:
                id: price
                multiline: False
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50 
        
        BoxLayout:
            size_hint: (0.95, 0.1)
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Quantity Available:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 50
                width: 300
            TextInput:
                id: quantity_available
                multiline: False
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 50

        BoxLayout:
            size_hint: (0.95, 0.2)
            orientation: 'horizontal'
            Label:
                halign: 'right'
                text: 'Description:'
                color: 0,0,0,1
                size_hint: (None, None)
                height: 200
                width: 300
            TextInput:
                id: description
                multiline: True
                cursor_color: (0,0,0,1)
                size_hint: (.2, None)
                height: 200

        BoxLayout:
            size_hint_y: 0.1  # Use a smaller portion of the screen for buttons
            padding: [10, 10]
            spacing: 10
            MDFlatButton:
                text: "Delete"
                id: delete
                on_press: root.delete()
                size_hint: (.1, None)

            Label:
                text: ''
                size_hint: (.8, None)

            MDFlatButton:
                text: "Cancel"
                on_press: root.cancel()
                size_hint: (.1, None)
            MDRaisedButton:
                text: "Save"
                style: "standard"
                on_press: root.save()
                size_hint: (.1, None)
"""

# Login screen class for handling user login
class LoginScreen(Screen):
    def run_login(self, username, password):
        """
        this function is run when the login button is pressed.
        runs the asynchronous function login until it is complete

        :param username: username
        :param password: password
        """
        loop.run_until_complete(self.login(username, password))

    async def login(self, username, password):
        """
        logs in by sending a log in request to the server with password and username by publishing to 
        the topic "AUTH_REQ/session_id" and subscribing to "AUT_RET/session_id" to listen to the result

        :param username: username
        :param password: password
        """
        print(f"Logging in with {username} and {password}")
        await c.publish(f"AUTH_REQ/{randomID}", int_to_bytes_str(f"{username}, {password}"), qos=0x01)
        await c.subscribe([(f"AUTH_RET/{randomID}", QOS_1)])

        message = await c.deliver_message()
        packet = message.publish_packet
        result = str(packet.payload.data)[12:-2]

        if result == "authorised":
            self.manager.current = 'adminScreen'
            self.manager.get_screen('adminScreen').c = c
        self.ids['username'].text = ""
        self.ids['password'].text = ""
        await c.unsubscribe([f"AUTH_RET/{randomID}"])

# Admin screen class for handling admin operations
class AdminScreen(Screen):
    def __init__(self, **kwargs):
        """
        Setting up of variables for the admin screen
        """
        # calling the __init()__ function of the class "Screen"
        super(AdminScreen, self).__init__(**kwargs)
        self.c = None
        self.camera_status = False

    def on_enter(self):
        """
        run load_table upon entering the admin screen
        """
        self.load_table()

    def reload(self):
        """
        reload table in admin screen by first removing the first table 
        and loading a new one
        """
        self.remove_widget(self.data_tables)
        self.load_table()

    def search(self, query):
        """
        search for keywords in the table by removing the first table
        and adding a new table with data that includes the search query

        :param query: the query to search the table entries for
        """
        self.remove_widget(self.data_tables)
        self.load_table_search(query)

    def load_table_search(self, query):
        """
        send a request to the server for items, filter through the items 
        creates a new table and adds it to the admin screen

        :param query: the query to search the table entries for
        """
        loop.run_until_complete(self.load_data())
        layout = BoxLayout(orientation='vertical')
        self.data = []
        for key in self.data_result:
            if query in str(key) or query in str(self.data_result[key]):
                self.data.append((
                    key,
                    self.data_result[key]['Product Name'],
                    self.data_result[key]['Category'],
                    self.data_result[key]['Description'],
                    self.data_result[key]['Price'],
                    self.data_result[key]['Quantity Available'],
                ))
        layout = BoxLayout(orientation='vertical')
        self.data_tables = MDDataTable(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=False,
            check=False,
            rows_num=len(self.data),
            column_data=[
                ("Product ID", dp(30)),
                ("Product Name", dp(50)),
                ("Category", dp(30)),
                ("Description", dp(90)),
                ("Price", dp(30)),
                ("Quantity Available", dp(30)), ],
            row_data=self.data)
        self.data_tables.bind(on_row_press=self.row_press)
        self.add_widget(self.data_tables)
        self.ids['search'].text = ""
        return layout
    
    def load_table(self):
        """
        requests data from the server and adds it to the table
        which is added into the admin screen
        """

        if hasattr(self, 'data_tables'):  # clears out old table
            self.remove_widget(self.data_tables)

        loop.run_until_complete(self.load_data())
        layout = BoxLayout(orientation='vertical')
        self.data_tables = MDDataTable(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=False,
            rows_num=len(self.data),
            column_data=[
                ("Product ID", dp(30)),
                ("Product Name", dp(50)),
                ("Category", dp(30)),
                ("Description", dp(90)),
                ("Price", dp(30)),
                ("Quantity Available", dp(30)), ],
            row_data=self.data)
        self.data_tables.bind(on_row_press=self.row_press)
        self.add_widget(self.data_tables)
        return layout
    
    def row_press(self, instance_table, instance_row):
        """
        this function is called when the row on the table is pressed
        the screen is switched to product screen and all the fields are preset 
        with the data of which the row is pressed. 

        :param instance_table: table instance which was pressed
        :param instance_row: row instance which was pressed
        """
        selected_row_index = instance_row.index // 6
        product_row = [str(i) for i in self.data[selected_row_index]]
        self.manager.current = 'productScreen'
        self.manager.get_screen('productScreen').c = c
        self.manager.get_screen('productScreen').product_id = product_row[0]
        self.manager.get_screen('productScreen').product_name = product_row[1]
        self.manager.get_screen('productScreen').category = product_row[2]
        self.manager.get_screen('productScreen').description = product_row[3]
        self.manager.get_screen('productScreen').price = product_row[4]
        self.manager.get_screen('productScreen').quantity_available = product_row[5]
        self.remove_widget(self.data_tables)

    async def load_data(self):
        """
        requests data from the server by requesting for data with the topic by publishing to
        "DATA_REQ/id_num" and subscribing to the server with the topic "DATA_RET/id_num" where 
        data is published back. 
        The data is then parsed into a list
        """
        await c.publish(f"DATA_REQ/{randomID}", int_to_bytes_str(f"data"), qos=0x01)
        await c.subscribe([(f"DATA_RET/{randomID}", QOS_1)])
        message = await c.deliver_message()
        packet = message.publish_packet
        result = str(packet.payload.data)[12:-2]
        self.data_result = json.loads(result)

        self.data = []
        for item in self.data_result:
            self.data.append((
                item,
                self.data_result[item]['Product Name'],
                self.data_result[item]['Category'],
                self.data_result[item]['Description'],
                self.data_result[item]['Price'],
                self.data_result[item]['Quantity Available'],
            ))

    def scan(self):
        """
        starts scanner if scanner is not switched on and stops the scanner
        if it is switched on

        to start scanner, an image is added to the admin screen and is updated 
        with a new image at 3fps using clock.schedule_interval

        to stop scanner, the clock.schedule_interval is stopped and the image
        widget is removed
        """
        if self.camera_status == False:
            self.s = scanner(0)
            self.image = Image(
                pos_hint={'center_y': 0.5, 'center_x': 0.5}
            )
            self.add_widget(self.image)
            Clock.schedule_interval(self.display_frame, 1.0 / 30.0)
            self.camera_status = True
        elif self.camera_status == True:
            Clock.unschedule(self.display_frame)
            self.s.stop()
            self.remove_widget(self.image)
            self.camera_status = False
    

    def display_frame(self, *args, **kwargs):
        """
        this uses the function from scan.py and returns a frame as well as any 
        code it detected if any. if code is detected, scan() is called to stop 
        the camera. 

        else, the frame is converted into a texture to be displayed on the Image 
        widget on the admin screen
        """
        code, frame = self.s.scan()
        buffer = cv2.flip(frame,0).tostring()
        texture1 = Texture.create(size=(frame.shape[1],frame.shape[0]), colorfmt='bgr') 
        texture1.blit_buffer(buffer, colorfmt='bgr',bufferfmt='ubyte')
        self.image.texture = texture1
        if code:
            self.product_found(code)
            self.scan() #switches off camera
    
    def product_found(self, code):
        """
        Checks whether the code is valid and displays the product screen page with all
        the fields filled in.

        else it shows an error. 

        :param code: code to display or check
        """
        product_id = code [-4:len(code)]
        item = self.s.code_check(product_id, self.data)
        if item == None:
            self.show_error("Invalid Code")
        else:
            self.manager.current = 'productScreen'
            self.manager.get_screen('productScreen').c = c
            self.manager.get_screen('productScreen').product_id = self.data[item][0]
            self.manager.get_screen('productScreen').product_name = self.data[item][1]
            self.manager.get_screen('productScreen').category = self.data[item][2]
            self.manager.get_screen('productScreen').description = self.data[item][3]
            self.manager.get_screen('productScreen').price = str(self.data[item][4])
            self.manager.get_screen('productScreen').quantity_available = str(self.data[item][5])
            self.remove_widget(self.data_tables)

    def show_error(self, error):
        """
        an error with the argument error is shown on kivy as a dialog

        :param error: error message to be displayed
        """
        self.dialog = MDDialog(
            title="Warning! Error",
            text=error,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    on_release=self.close_dialog
                ),
            ],
            auto_dismiss=False
        )
        self.dialog.open()
    
    def close_dialog(self, *args):
        """
        this function is called when the "OK" button on the error dialog 
        is pressed to close the dialog
        """
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    
    def add(self):
        """
        this function is called when the plus button on the admin screen is pressed 
        to add a new product.
        """
        self.manager.current = 'productScreen'
        self.manager.get_screen('productScreen').c = c
        self.manager.get_screen('productScreen').ids['product_id'].readonly = False
        self.manager.get_screen('productScreen').new = True
        self.manager.get_screen('productScreen').ids['delete'].disabled = True
        self.remove_widget(self.data_tables)


class ProductScreen(Screen):
    def __init__(self, **kwargs):
        """
        initliatise product screen
        """
        super(ProductScreen, self).__init__(**kwargs)
        self.new = False  # determines if "new" button is pressed
        self.reset_field()  # reset all fields

    def cancel(self):
        """
        this function is called when the cancel button is pressed. the screen changes back to 
        admin screen and all fields are reset. 
        """
        self.reset_field()
        self.manager.current = 'adminScreen'
        self.manager.get_screen('adminScreen').c = c
        self.ids['product_id'].readonly = True
        self.new = False
        self.ids['delete'].disabled = False

    def reset_field(self):
        """
        reset all input fields to blank
        """
        self.product_id = ""
        self.product_name = ""
        self.category = ""
        self.description = ""
        self.price = ""
        self.quantity_available = ""
    
    def on_enter(self, *args):
        """
        preset all the input fields to either 
        1. nothing when an item is getting added
        2. the respective data when an item is getting changed
        """
        self.ids['product_id'].text = self.product_id
        self.ids['product_name'].text = self.product_name
        self.ids['category'].text = self.category
        self.ids['description'].text = self.description
        self.ids['price'].text = self.price
        self.ids['quantity_available'].text = self.quantity_available

    def save(self):
        """
        this function is ran when the "save" button is pressed. 
        it is sent to the server and listens to any errors sent back 
        from the server. the error will be shown if there are any. 
        """
        loop.run_until_complete(self.publish_new())
        error = loop.run_until_complete(self.error_check())
        if error == "None":
            self.reset_field()
            self.manager.current = 'adminScreen'
            self.manager.get_screen('adminScreen').c = c
            self.ids['product_id'].readonly = True
            self.new = False
            self.ids['delete'].disabled = False
        else:
            self.show_error(error) 

    async def publish_new(self):
        """
        parses the data in the input fields into a list which is converted into
        a json text and published to the server. the data is published to add a product
        OR to change a certain product 
        """
        new_data = {
            "Product ID": self.ids['product_id'].text,
            "Product Name" : self.ids['product_name'].text,
            "Category" : self.ids['category'].text,
            "Description" : self.ids['description'].text,
            "Price" : self.ids['price'].text,
            "Quantity Available" : self.ids['quantity_available'].text
        }
        if self.new:
            await c.publish(f"DATA_NEW/{randomID}", int_to_bytes_str(json.dumps(new_data)),qos=0x01)
        else:
            await c.publish(f"DATA_PUB/{randomID}", int_to_bytes_str(json.dumps(new_data)),qos=0x01)
    
    async def error_check(self):
        """
        subscribes to the topic "DATA_ERROR/session_id" which will return the status of the data publish
        or the data new publication and any erorrs that occur. 
        """
        await c.subscribe([(f"DATA_ERROR/{randomID}", QOS_1)])
        message = await c.deliver_message()
        packet = message.publish_packet
        result = str(packet.payload.data)[12:-2]
        return result
    
    def show_error(self, error):
        """
        an error with the argument error is shown on kivy as a dialog

        :param error: error message to be displayed
        """
        self.dialog = MDDialog(
            title="Warning! Error",
            text=error,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    on_release=self.close_dialog
                ),
            ],
            auto_dismiss=False
        )
        self.dialog.open()
    
    def close_dialog(self, *args):
        """
        this function is called when the "OK" button on the error dialog 
        is pressed to close the dialog
        """
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

    def delete(self):
        """
        this function is run when the "delete" button on the product screen is pressed. 
        """
        loop.run_until_complete(self.delete_data(self.ids['product_id'].text))

    async def delete_data(self, product_id):
        """
        publishes to DATA/DEL and sends the product ID of the item to delete. 
        changes screen back to admin screen

        :param product_id: product id to delete
        """
        await c.publish(f"DATA_DEL/{randomID}", int_to_bytes_str(product_id),qos=0x01)
        self.reset_field()
        self.manager.current = 'adminScreen'
        self.manager.get_screen('adminScreen').c = c
        self.ids['product_id'].readonly = True
        self.new = False
        self.ids['delete'].disabled = False

class LoginApp(MDApp):
    async def uptime_coro(self):
        """
        connects the client to the server. uses a standard username and password. 

        makes c global so it can be accessed accross screens. 
        """
        global c
        c = MQTTClient()
        try:
            await c.connect(f"mqtt://auth_handler:auth_handler@{SERVER_IP}:1883")
        except ClientException as ce:
            logger.error("Client exception: %s" % ce)

    def build(self):
        """
        set up screenmanager
        """
        manager = ScreenManager(transition=NoTransition())
        manager.add_widget(LoginScreen(name="loginScreen"))
        manager.add_widget(AdminScreen(name="adminScreen"))
        manager.add_widget(ProductScreen(name="productScreen"))
        return manager

    def on_start(self):
        """
        makes loop and randomID global so it can be accessed accross screen

        set up asyncio as well as kivy clock to run cocurrently to support kivy ui
        and amqtt message handling. 

        every 0.1 seconds, kivy clock will run run_asyncio_loop to give chance for asyncio amqtt message
        handling to work. 
        """
        # Start the asyncio event loop when the app starts
        global loop
        loop = asyncio.get_event_loop()
        global randomID
        randomID = random_ID_gen()
        loop.run_until_complete(self.uptime_coro())
        self.asyncio_loop_task = Clock.schedule_interval(self.run_asyncio_loop, 0.1)

    def run_asyncio_loop(self, *args):
        """
        stops the loop temporarily
        runs the asyncio loop
        """
        loop.stop()
        loop.run_forever()

    def on_stop(self):
        """
        these functions run when the app ends
        the kivy clock is stopped and asyncio stops 
        """
        # Stop the asyncio event loop when the app stops
        loop.stop()
        self.asyncio_loop_task.cancel()

def random_ID_gen():
    """
    generates a random ID for session ID 
    """
    character = "abcdefghijklmnopqrstupwxyz1234567890"
    auth_id = ""
    for i in range(5):
        auth_id += character[random.randint(0,24)]
    return auth_id

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Build the Kivy UI from the kv string
    Window.clearcolor = (241, 248, 232, 1)
    Builder.load_string(kv_string)
    Window.fullscreen = 'auto'

    LoginApp().run()