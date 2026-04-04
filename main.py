from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Frt Design APK Build System", font_size='20sp')
        
        # Connects the button to the on_click function
        btn = Button(text="Test Connection", size_hint=(1, 0.2))
        btn.bind(on_press=self.on_click)
        
        layout.add_widget(self.label)
        layout.add_widget(btn)
        return layout

    # This function must be named on_click
    def on_click(self, instance):
        self.label.text = "Status: Online & Working!"

if __name__ == "__main__":
    MainApp().run()
