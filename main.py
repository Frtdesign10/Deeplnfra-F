from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Bir başlık ekleyelim
        self.label = Label(text="Frt Design APK Testi", font_size='24sp')
        
        # Bir buton ekleyelim
        btn = Button(text="Tıkla Bakalım", size_hint=(1, 0.2))
        btn.bind(on_press=self.on_button_click)
        
        layout.add_widget(self.label)
        layout.add_widget(btn)
        
        return layout

    def on_button_click(self, instance):
        self.label.text = "Kod Başarıyla Çalıştı!"

if __name__ == "__main__":
    TestApp().run()
