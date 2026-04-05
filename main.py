from kivy.app import App
from kivy.uix.button import Button

class MainApp(App):
    def build(self):
        # En basit buton: Tıklayınca metni değişir
        return Button(text="Hello from Mardin! Click me.", on_release=self.change_text)

    def change_text(self, instance):
        instance.text = "Build Successful!"

if __name__ == "__main__":
    MainApp().run()
