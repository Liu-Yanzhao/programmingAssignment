import logging
from manage.authentication import authentication

from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
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
        orientation: 'vertical'
        padding: 2
        Label:
            text: 'admin screen'
            color: 0,0,0,1

<DevScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 2
        Label:
            text: "devScreen"
            color: 0,0,0,1
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

    def admin(self):
        print("admin screen")
        
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