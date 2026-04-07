from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.core.window import Window

class FrtDesignApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.status_label = MDLabel(
            text="FRT DESIGN SYSTEM",
            halign="center",
            font_style="H4"
        )
        
        btn = MDRaisedButton(
            text="START CONNECTION TEST",
            pos_hint={"center_x": .5},
            on_release=self.on_button_click
        )
        
        layout.add_widget(self.status_label)
        layout.add_widget(btn)
        return layout

    def on_button_click(self, instance):
        self.status_label.text = "SYSTEM ONLINE"
        self.status_label.text_color = (0, 1, 0, 1)

if __name__ == "__main__":
    FrtDesignApp().run()
    
    
    
