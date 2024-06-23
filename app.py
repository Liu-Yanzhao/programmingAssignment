import logging

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.core.window import Window
from kivy.lang import Builder

LOGFILE = "manage/data/history.log"

kv_string = """
<LoginScreen>:
    orientation: 'vertical'
    padding: 20
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
"""

class programLogging:
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

class LoginScreen(BoxLayout):
    def login(self, username, password):
        # Add your login logic here
        print(f"Logging in with {username} and {password}")

class LoginApp(App):
    def build(self):
        return LoginScreen()

if __name__ == '__main__':
    programLogging()
    LoginApp().run()