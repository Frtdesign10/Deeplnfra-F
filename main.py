from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
import threading
import socket

Window.clearcolor = (0.05, 0.05, 0.05, 1)


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"

        layout = MDBoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        self.title_label = MDLabel(
            text="FRT DESIGN SYSTEM",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            opacity=0
        )

        self.status_label = MDLabel(
            text="Sistem bekleniyor...",
            halign="center",
            font_style="H6",
            theme_text_color="Secondary"
        )

        self.sub_label = MDLabel(
            text="Bağlantı testi için butona bas",
            halign="center",
            font_style="Caption",
            theme_text_color="Hint"
        )

        self.test_btn = MDRaisedButton(
            text="START CONNECTION TEST",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.1, 0.5, 1, 1),
            on_release=self.start_test
        )

        self.detail_btn = MDRaisedButton(
            text="DETAYLAR",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.2, 0.2, 1),
            on_release=self.go_details
        )

        layout.add_widget(self.title_label)
        layout.add_widget(self.status_label)
        layout.add_widget(self.sub_label)
        layout.add_widget(self.test_btn)
        layout.add_widget(self.detail_btn)
        self.add_widget(layout)

        Clock.schedule_once(self.animate_in, 0.5)

    def animate_in(self, dt):
        Animation(opacity=1, duration=1.2).start(self.title_label)

    def start_test(self, instance):
        self.test_btn.disabled = True
        self.status_label.text = "⏳ Test ediliyor..."
        self.status_label.theme_text_color = "Secondary"
        self.sub_label.text = "Lütfen bekleyin..."
        threading.Thread(target=self.run_test, daemon=True).start()

    def run_test(self):
        results = {}
        hosts = {
            "Google": ("8.8.8.8", 53),
            "Cloudflare": ("1.1.1.1", 53),
            "Internet": ("google.com", 80)
        }
        for name, (host, port) in hosts.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((host, port))
                s.close()
                results[name] = True
            except Exception:
                results[name] = False

        Clock.schedule_once(lambda dt: self.show_results(results), 0)

    def show_results(self, results):
        self.test_btn.disabled = False
        all_ok = all(results.values())

        if all_ok:
            self.status_label.text = "✅ SYSTEM ONLINE"
            self.status_label.theme_text_color = "Custom"
            self.status_label.text_color = (0, 1, 0.4, 1)
            self.sub_label.text = "Tüm bağlantılar başarılı"
        else:
            failed = [k for k, v in results.items() if not v]
            self.status_label.text = "⚠️ BAĞLANTI SORUNU"
            self.status_label.theme_text_color = "Custom"
            self.status_label.text_color = (1, 0.5, 0, 1)
            self.sub_label.text = "Başarısız: " + ", ".join(failed)

        detail = self.manager.get_screen("detail")
        detail.update_results(results)

    def go_details(self, instance):
        self.manager.current = "detail"


class DetailScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "detail"

        layout = MDBoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        title = MDLabel(
            text="BAĞLANTI DETAYLARI",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )

        self.google_lbl = MDLabel(
            text="Google DNS  :  —",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary"
        )
        self.cloudflare_lbl = MDLabel(
            text="Cloudflare   :  —",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary"
        )
        self.internet_lbl = MDLabel(
            text="Internet       :  —",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary"
        )

        back_btn = MDRaisedButton(
            text="GERİ DÖN",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.2, 0.2, 1),
            on_release=self.go_back
        )

        layout.add_widget(title)
        layout.add_widget(self.google_lbl)
        layout.add_widget(self.cloudflare_lbl)
        layout.add_widget(self.internet_lbl)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def update_results(self, results):
        labels = {
            "Google": self.google_lbl,
            "Cloudflare": self.cloudflare_lbl,
            "Internet": self.internet_lbl
        }
        names = {
            "Google": "Google DNS ",
            "Cloudflare": "Cloudflare  ",
            "Internet": "Internet    "
        }
        for key, lbl in labels.items():
            ok = results.get(key, False)
            status = "✅ OK" if ok else "❌ FAIL"
            lbl.text = f"{names[key]} :  {status}"
            lbl.theme_text_color = "Custom"
            lbl.text_color = (0, 1, 0.4, 1) if ok else (1, 0.4, 0, 1)

    def go_back(self, instance):
        self.manager.current = "home"


class FrtDesignApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        sm = MDScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(DetailScreen())
        return sm


if __name__ == "__main__":
    FrtDesignApp().run()
