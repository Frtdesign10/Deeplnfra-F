from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.card import MDCard
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
import threading
import socket

Window.clearcolor = (0.05, 0.05, 0.05, 1)


# ─────────────────────────────────────────
#  EKRAN 1 – Ana Ekran
# ─────────────────────────────────────────
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"

        layout = MDBoxLayout(
            orientation="vertical",
            padding=30,
            spacing=24
        )

        # Başlık
        self.title_label = MDLabel(
            text="FRT DESIGN SYSTEM",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            opacity=0
        )

        # Kart
        card = MDCard(
            orientation="vertical",
            padding=20,
            spacing=12,
            size_hint=(1, None),
            height=180,
            md_bg_color=(0.15, 0.15, 0.15, 1),
            radius=[16]
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

        card.add_widget(self.status_label)
        card.add_widget(self.sub_label)

        # Loading göstergesi
        self.spinner = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=("48dp", "48dp"),
            pos_hint={"center_x": 0.5},
            opacity=0
        )

        # Butonlar
        self.test_btn = MDRaisedButton(
            text="START CONNECTION TEST",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.1, 0.5, 1, 1),
            on_release=self.start_test
        )

        detail_btn = MDRaisedButton(
            text="DETAYLAR",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.2, 0.2, 1),
            on_release=self.go_details
        )

        layout.add_widget(self.title_label)
        layout.add_widget(card)
        layout.add_widget(self.spinner)
        layout.add_widget(self.test_btn)
        layout.add_widget(detail_btn)
        self.add_widget(layout)

        # Giriş animasyonu
        Clock.schedule_once(self.animate_in, 0.3)

    def animate_in(self, dt):
        anim = Animation(opacity=1, duration=1.2)
        anim.start(self.title_label)

    def start_test(self, instance):
        self.test_btn.disabled = True
        self.spinner.opacity = 1
        self.status_label.text = "Test ediliyor..."
        self.status_label.theme_text_color = "Secondary"
        self.sub_label.text = "Lütfen bekleyin..."
        threading.Thread(target=self.run_test, daemon=True).start()

    def run_test(self):
        results = {}
        hosts = {
            "Google": "8.8.8.8",
            "Cloudflare": "1.1.1.1",
            "Internet": "google.com"
        }
        for name, host in hosts.items():
            try:
                socket.setdefaulttimeout(3)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 53))
                results[name] = True
            except Exception:
                results[name] = False

        Clock.schedule_once(lambda dt: self.show_results(results), 0)

    def show_results(self, results):
        self.spinner.opacity = 0
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
            self.sub_label.text = f"Başarısız: {', '.join(failed)}"

        detail = self.manager.get_screen("detail")
        detail.update_results(results)

        anim = (
            Animation(pos_hint={"center_x": 0.52}, duration=0.05) +
            Animation(pos_hint={"center_x": 0.48}, duration=0.05) +
            Animation(pos_hint={"center_x": 0.5}, duration=0.05)
        )
        anim.start(self.status_label)

    def go_details(self, instance):
        self.manager.current = "detail"


# ─────────────────────────────────────────
#  EKRAN 2 – Detay Ekranı
# ─────────────────────────────────────────
class DetailScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "detail"

        layout = MDBoxLayout(
            orientation="vertical",
            padding=30,
            spacing=16
        )

        title = MDLabel(
            text="BAĞLANTI DETAYLARI",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )

        self.google_lbl = MDLabel(
            text="Google DNS : —",
            halign="center",
            font_style="Body1"
        )
        self.cloudflare_lbl = MDLabel(
            text="Cloudflare  : —",
            halign="center",
            font_style="Body1"
        )
        self.internet_lbl = MDLabel(
            text="Internet    : —",
            halign="center",
            font_style="Body1"
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
        def fmt(name, key):
            ok = results.get(key, False)
            color = "[color=00ff66]✅ OK[/color]" if ok else "[color=ff6600]❌ FAIL[/color]"
            return f"{name} : {color}"

        self.google_lbl.text = fmt("Google DNS ", "Google")
        self.google_lbl.markup = True
        self.cloudflare_lbl.text = fmt("Cloudflare ", "Cloudflare")
        self.cloudflare_lbl.markup = True
        self.internet_lbl.text = fmt("Internet   ", "Internet")
        self.internet_lbl.markup = True

    def go_back(self, instance):
        self.manager.current = "home"


# ─────────────────────────────────────────
#  ANA UYGULAMA
# ─────────────────────────────────────────
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
