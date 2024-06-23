import logging
from manage.authentication import authentication

from kivymd.app import MDApp
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, ObjectProperty

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
                on_press: root.login(username.text, password.text)

<AdminScreen>:
    BoxLayout:
        pos: 0, 1820
        Label:
            text: 'Admin Dashboard'
            color: 0,0,0,1
            size_hint: (.2, None)
 
        MDIconButton:
            icon: "exit-to-app"
            style: "standard"

    # Label:
    #     text: "hi"       
    #     color: 0,0,0,1


<DevScreen>:
    Label:
        text: "devScreen"
        color: 0,0,0,1
        pos_hint:{'x':0, 'y':0}
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

Window.clearcolor = (241, 248, 232, 1)
Builder.load_string(kv_string)
Window.fullscreen = 'auto'

class LoginScreen(Screen):
    def login(self, username, password):
        print(f"Logging in with {username} and {password}")
        auth = authentication(username, password)
        result, c = auth.start_client()
        if result == "unauthorised":
            self.ids['username'].text = ""
            self.ids['password'].text = ""
        elif result == "admin":
            self.manager.current = 'adminScreen'
            self.manager.get_screen('adminScreen').c = c
        elif result == "dev":
            self.manager.current = 'devScreen'
            self.manager.get_screen('devScreen').c = c

class AdminScreen(Screen):
    c = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(AdminScreen, self).__init__(**kwargs)
        self.c = None

    def on_enter(self):
        self.load_table()
    
    def load_table(self):
        layout = AnchorLayout()
        self.load_data()
        self.data_tables = MDDataTable(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=True,
            check=True,
            column_data=[
                ("Product ID", dp(30)),
                ("Product Name", dp(50)),
                ("Category", dp(30)),
                ("Description", dp(90)),
                ("Price", dp(30)),
                ("Quantity Available", dp(30)), ],
            row_data=self.data)
        self.add_widget(self.data_tables)
        return layout
    
    def load_data(self):
        self.data = []
        for item in self.c.products:
            self.data.append((
                item,
                self.c.products[item]['Product Name'],
                self.c.products[item]['Category'],
                self.c.products[item]['Description'],
                self.c.products[item]['Price'],
                self.c.products[item]['Quantity Available'],
            ))

        
class DevScreen(Screen):
    c = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DevScreen, self).__init__(**kwargs)
        self.c = None

    def developer(self):
        print("developer screen")

class LoginApp(MDApp):
    def build(self):
        manager = ScreenManager(transition=NoTransition())
        manager.add_widget(LoginScreen(name="loginScreen"))
        manager.add_widget(AdminScreen(name="adminScreen"))
        manager.add_widget(DevScreen(name="devScreen"))
        return manager

if __name__ == '__main__':
    programLogging()
    LoginApp().run()