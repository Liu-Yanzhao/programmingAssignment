from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.core.window import Window
from kivy.lang import Builder


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
    LoginApp().run()