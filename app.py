import logging
import random
# from listener import listener
import asyncio
import json
import cv2
from kivy.uix.image import Image
from manage.scanner import scanner

from amqtt.client import MQTTClient, ClientException
from amqtt.codecs import int_to_bytes_str
from amqtt.mqtt.constants import QOS_1, QOS_2
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, ObjectProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import kivy
from kivy.core.window import Window
from kivy.lang import Builder

LOGFILE = "manage/data/history.log"

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

class programLogging():
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        #formats
        format = logging.Formatter(" [%(levelname)s\t] :: %(asctime)s :: %(name)s :: %(message)s")
        program_run = logging.Formatter(
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"+
            ":::::::: %(asctime)s :: %(message)s ::::::::\n"+
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            )

        #setting up program run banner
        newentry = logging.FileHandler(LOGFILE)
        newentry.setLevel(logging.DEBUG)
        newentry.setFormatter(program_run)
        self.logger.addHandler(newentry)
        self.logger.removeHandler(newentry)

        #setting up file logging
        file = logging.FileHandler(LOGFILE)
        file.setLevel(logging.INFO)
        file.setFormatter(format)
        self.logger.addHandler(file)

class LoginScreen(Screen):
    def run_login(self, username, password):
        loop.run_until_complete(self.login(username, password))

    async def login(self, username, password):
        # print(f"Logging in with {username} and {password}")
        # await c.publish(f"AUTH_REQ/{randomID}", int_to_bytes_str(f"{username}, {password}"), qos=0x01)
        # await c.subscribe([(f"AUTH_RET/{randomID}", QOS_1)])

        # message = await c.deliver_message()
        # packet = message.publish_packet
        # result = str(packet.payload.data)[12:-2]

        # if result == "authorised":
        #     self.manager.current = 'adminScreen'
        #     self.manager.get_screen('adminScreen').c = c
        # self.ids['username'].text = ""
        # self.ids['password'].text = ""
        # await c.unsubscribe([f"AUTH_RET/{randomID}"])
        self.manager.current = 'adminScreen'
        self.manager.get_screen('adminScreen').c = c

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super(AdminScreen, self).__init__(**kwargs)
        self.c = None
        self.camera_status = False

    def on_enter(self):
        self.load_table()

    def reload(self):
        self.remove_widget(self.data_tables)
        self.load_table()

    def search(self, query):
        self.remove_widget(self.data_tables)
        self.load_table_search(query)

    def load_table_search(self, query):
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
            use_pagination=True,
            check=False,
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
        loop.run_until_complete(self.load_data())
        layout = BoxLayout(orientation='vertical')
        self.data_tables = MDDataTable(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=True,
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

    async def load_data(self):
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
        if self.camera_status == False:
            self.s = scanner(0, 1, 'Scanner')
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
        code, frame = self.s.scan()
        buffer = cv2.flip(frame,0).tostring()
        texture1 = Texture.create(size=(frame.shape[1],frame.shape[0]), colorfmt='bgr') 
        texture1.blit_buffer(buffer, colorfmt='bgr',bufferfmt='ubyte')
        self.image.texture = texture1
        if code:
            self.product_found(code)
            self.scan() #switches off camera
    
    def product_found(self, code):
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

    def show_error(self, error):
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
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    
    def add(self):
        self.manager.current = 'productScreen'
        self.manager.get_screen('productScreen').c = c
        self.manager.get_screen('productScreen').ids['product_id'].readonly = False
        self.manager.get_screen('productScreen').new = True
        self.manager.get_screen('productScreen').ids['delete'].disabled = True


class ProductScreen(Screen):
    def __init__(self, **kwargs):
        super(ProductScreen, self).__init__(**kwargs)
        self.new = False
        self.reset_field() 

    def cancel(self):
        self.reset_field()
        self.manager.current = 'adminScreen'
        self.manager.get_screen('adminScreen').c = c
        self.ids['product_id'].readonly = True
        self.new = False
        self.ids['delete'].disabled = False

    def reset_field(self):
        self.product_id = ""
        self.product_name = ""
        self.category = ""
        self.description = ""
        self.price = ""
        self.quantity_available = ""
    
    def on_enter(self, *args):
        self.ids['product_id'].text = self.product_id
        self.ids['product_name'].text = self.product_name
        self.ids['category'].text = self.category
        self.ids['description'].text = self.description
        self.ids['price'].text = self.price
        self.ids['quantity_available'].text = self.quantity_available

    def save(self):
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
        await c.subscribe([(f"DATA_ERROR/{randomID}", QOS_1)])
        message = await c.deliver_message()
        packet = message.publish_packet
        result = str(packet.payload.data)[12:-2]
        return result
    
    def show_error(self, error):
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
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

    def delete(self):
        loop.run_until_complete(self.delete_data(self.ids['product_id'].text))

    async def delete_data(self, product_id):
        await c.publish(f"DATA_DEL/{randomID}", int_to_bytes_str(product_id),qos=0x01)
        self.reset_field()
        self.manager.current = 'adminScreen'
        self.manager.get_screen('adminScreen').c = c
        self.ids['product_id'].readonly = True
        self.new = False
        self.ids['delete'].disabled = False

class LoginApp(MDApp):
    async def uptime_coro(self):
        global c
        c = MQTTClient()
        try:
            await c.connect("mqtt://auth_handler:auth_handler@127.0.0.1:1883")
        except ClientException as ce:
            logger.error("Client exception: %s" % ce)

    def build(self):
        manager = ScreenManager(transition=NoTransition())
        manager.add_widget(LoginScreen(name="loginScreen"))
        manager.add_widget(AdminScreen(name="adminScreen"))
        manager.add_widget(ProductScreen(name="productScreen"))
        return manager

    def on_start(self):
        # Start the asyncio event loop when the app starts
        global loop
        loop = asyncio.get_event_loop()
        global randomID
        randomID = random_ID_gen()
        loop.run_until_complete(self.uptime_coro())
        self.asyncio_loop_task = Clock.schedule_interval(self.run_asyncio_loop, 0.1)

    def run_asyncio_loop(self, *args):
        loop.stop()
        loop.run_forever()

    def on_stop(self):
        # Stop the asyncio event loop when the app stops
        loop.stop()
        self.asyncio_loop_task.cancel()

def random_ID_gen():
    character = "abcdefghijklmnopqrstupwxyz1234567890"
    auth_id = ""
    for i in range(5):
        auth_id += character[random.randint(0,24)]
    return auth_id

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    Window.clearcolor = (241, 248, 232, 1)
    Builder.load_string(kv_string)
    # Window.fullscreen = 'auto'
    programLogging()
    LoginApp().run()