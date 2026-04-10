
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder

KV = """
MDScreen:
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "12dp"

        MDLabel:
            text: "Merhaba KivyMD!"
            halign: "center"
            font_style: "H4"

        MDRaisedButton:
            text: "Tıkla"
            pos_hint: {"center_x": 0.5}
            on_release: app.button_pressed()
"""

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def button_pressed(self):
        print("Butona tıklandı!")

if __name__ == "__main__":
    MainApp().run()

    
    
    
