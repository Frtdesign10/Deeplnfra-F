"""
KOSTEBEK-AR
GPS Tabanlı AR Altyapı Görselleştirme Sistemi
Geliştirici: FRT Design
"""

APP_VERSION = "2026.04.12"

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.camera import Camera
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
import threading
import json
import os
import math

Window.clearcolor = (0.03, 0.03, 0.03, 1)

# ─────────────────────────────────────────
#  GPS YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────

def gps_to_screen(hat_lat, hat_lon, my_lat, my_lon, screen_w, screen_h, scale=50000):
    dlat = hat_lat - my_lat
    dlon = hat_lon - my_lon
    dx = dlon * 111320 * math.cos(math.radians(my_lat))
    dy = dlat * 111320
    px = screen_w / 2 + dx * (scale / 111320)
    py = screen_h / 2 - dy * (scale / 111320)
    return px, py


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ─────────────────────────────────────────
#  VERİTABANI
# ─────────────────────────────────────────

DEFAULT_HATLAR = [
    {
        "id": 1,
        "name": "Ana Dogalgaz Hatti",
        "type": "DOGALGAZ",
        "company": "IGDAS",
        "depth_cm": 150,
        "pressure": "4 bar",
        "year": 2008,
        "coordinates": [
            {"lat": 41.01500, "lon": 28.97900},
            {"lat": 41.01500, "lon": 28.98200}
        ],
        "color": [0, 1, 1, 0.85],
        "thickness": 8
    },
    {
        "id": 2,
        "name": "Su Ana Boru Hatti",
        "type": "SU HATTI",
        "company": "ISKI",
        "depth_cm": 80,
        "pressure": "2.5 bar",
        "year": 2015,
        "coordinates": [
            {"lat": 41.01480, "lon": 28.98050},
            {"lat": 41.01550, "lon": 28.98050}
        ],
        "color": [0.2, 0.5, 1, 0.85],
        "thickness": 6
    },
    {
        "id": 3,
        "name": "Yuksek Gerilim Hatti",
        "type": "ELEKTRIK",
        "company": "BEDAS",
        "depth_cm": 60,
        "voltage": "380V",
        "year": 2012,
        "coordinates": [
            {"lat": 41.01460, "lon": 28.97950},
            {"lat": 41.01460, "lon": 28.98150}
        ],
        "color": [1, 0.85, 0, 0.85],
        "thickness": 5
    },
    {
        "id": 4,
        "name": "Fiber Optik Omurga",
        "type": "FIBER OPTIK",
        "company": "TURK TELEKOM",
        "depth_cm": 40,
        "bandwidth": "10 Gbps",
        "year": 2019,
        "coordinates": [
            {"lat": 41.01510, "lon": 28.97920},
            {"lat": 41.01510, "lon": 28.98180}
        ],
        "color": [0.4, 1, 0.4, 0.85],
        "thickness": 4
    },
]

DB_PATH = "/sdcard/kostebek_hatlar.json"

def load_hatlar():
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data
    except Exception as e:
        print("JSON yukleme hatasi:", e)
    return list(DEFAULT_HATLAR)

def save_hatlar(hatlar):
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(hatlar, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("JSON kaydetme hatasi:", e)
        return False

def fetch_hatlar_from_api(api_url):
    try:
        import urllib.request
        with urllib.request.urlopen(api_url, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print("API hatasi:", e)
        return None


# ─────────────────────────────────────────
#  GPS MODÜLÜ
# ─────────────────────────────────────────

class GPSManager:
    def __init__(self):
        self.lat = 41.01500
        self.lon = 28.98050
        self.accuracy = 0
        self.running = False
        self._try_android_gps()

    def _try_android_gps(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION])
            from plyer import gps
            self.gps = gps
            gps.configure(on_location=self._on_location)
            gps.start(minTime=1000, minDistance=0.5)
            self.running = True
        except Exception as e:
            print("GPS simulasyon modu:", e)
            self.running = False

    def _on_location(self, **kwargs):
        self.lat = kwargs.get("lat", self.lat)
        self.lon = kwargs.get("lon", self.lon)
        self.accuracy = kwargs.get("accuracy", 0)

    def get_location(self):
        return self.lat, self.lon, self.accuracy

    def stop(self):
        try:
            if self.running:
                self.gps.stop()
        except:
            pass


# ─────────────────────────────────────────
#  AR OVERLAY
# ─────────────────────────────────────────

class AROverlay(Widget):
    def __init__(self, gps_manager, **kwargs):
        super().__init__(**kwargs)
        self.gps = gps_manager
        self.hatlar = load_hatlar()
        self.touch_pos = (0, 0)
        self.blink_state = True
        self.danger_active = False
        self.closest_hat = None
        self.on_danger_change = None
        self.on_hat_select = None
        self.scale = 50000
        Clock.schedule_interval(self.tick, 0.4)
        self.bind(size=self.redraw, pos=self.redraw)

    def tick(self, dt):
        self.blink_state = not self.blink_state
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        w, h = self.size
        if w == 0 or h == 0:
            return

        my_lat, my_lon, accuracy = self.gps.get_location()
        danger = False
        closest = None
        closest_dist = 9999

        with self.canvas:
            for hat in self.hatlar:
                coords = hat.get("coordinates", [])
                if len(coords) < 2:
                    continue

                for i in range(len(coords) - 1):
                    p1 = gps_to_screen(
                        coords[i]["lat"], coords[i]["lon"],
                        my_lat, my_lon, w, h, self.scale
                    )
                    p2 = gps_to_screen(
                        coords[i+1]["lat"], coords[i+1]["lon"],
                        my_lat, my_lon, w, h, self.scale
                    )

                    dist = self._line_distance(p1, p2, self.touch_pos)
                    is_close = dist < 45

                    if is_close:
                        danger = True
                        if dist < closest_dist:
                            closest_dist = dist
                            closest = hat

                    r, g, b, a = hat["color"]
                    thick = hat.get("thickness", 5)

                    if is_close and self.blink_state:
                        Color(1, 0.1, 0.1, 1)
                        Line(points=[p1[0], p1[1], p2[0], p2[1]], width=thick * 2.8)
                    else:
                        Color(r, g, b, a)
                        Line(points=[p1[0], p1[1], p2[0], p2[1]], width=thick)

                    # Nokta
                    Color(1, 1, 1, 0.5)
                    Ellipse(pos=(p1[0]-5, p1[1]-5), size=(10, 10))

                    # Etiket arka plan
                    mid_x = (p1[0] + p2[0]) / 2
                    mid_y = (p1[1] + p2[1]) / 2
                    Color(0, 0, 0, 0.65)
                    Rectangle(pos=(mid_x - 65, mid_y + 5), size=(130, 20))

            # Kullanıcı konumu
            Color(0.2, 0.6, 1, 1)
            Ellipse(pos=(w/2 - 10, h/2 - 10), size=(20, 20))
            Color(0.2, 0.6, 1, 0.25)
            Ellipse(pos=(w/2 - 28, h/2 - 28), size=(56, 56))

            # GPS doğruluk çemberi
            if accuracy > 0:
                acc_px = accuracy * (self.scale / 111320)
                Color(0.2, 0.6, 1, 0.12)
                Ellipse(pos=(w/2 - acc_px, h/2 - acc_px), size=(acc_px*2, acc_px*2))

            # Tehlike çerçevesi
            if danger and self.blink_state:
                Color(1, 0, 0, 0.7)
                Line(rectangle=(3, 3, w-6, h-6), width=7)

        self.closest_hat = closest
        self.danger_active = danger
        if self.on_danger_change:
            self.on_danger_change(danger, closest)

    def _line_distance(self, p1, p2, point):
        x1, y1 = p1
        x2, y2 = p2
        px, py = point
        dx, dy = x2-x1, y2-y1
        if dx == 0 and dy == 0:
            return math.hypot(px-x1, py-y1)
        t = max(0, min(1, ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)))
        return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

    def on_touch_move(self, touch):
        self.touch_pos = (touch.x, touch.y - self.y)
        self.redraw()
        return True

    def on_touch_down(self, touch):
        self.touch_pos = (touch.x, touch.y - self.y)
        self.redraw()
        if self.closest_hat and self.on_hat_select:
            self.on_hat_select(self.closest_hat)
        return True

    def zoom_in(self):
        self.scale = min(self.scale * 1.3, 500000)
        self.redraw()

    def zoom_out(self):
        self.scale = max(self.scale / 1.3, 5000)
        self.redraw()

    def reload_hatlar(self):
        self.hatlar = load_hatlar()
        self.redraw()


# ─────────────────────────────────────────
#  EKRAN 1 – AR KAMERA
# ─────────────────────────────────────────

class ARScreen(MDScreen):
    def __init__(self, gps_manager, **kwargs):
        super().__init__(**kwargs)
        self.name = "ar"
        self.gps = gps_manager
        self.dialog = None

        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title=f"KOSTEBEK-AR  {APP_VERSION}",
            right_action_items=[
                ["database-edit", lambda x: setattr(self.manager, "current", "db")],
                ["format-list-bulleted", lambda x: setattr(self.manager, "current", "list")],
                ["information-outline", lambda x: setattr(self.manager, "current", "info")],
            ]
        )

        cam_box = MDBoxLayout()
        try:
            self.camera = Camera(play=True, index=0, size_hint=(1, 1))
            cam_box.add_widget(self.camera)
        except:
            cam_box.add_widget(MDLabel(text="[Kamera yok - Simulasyon]", halign="center"))

        self.overlay = AROverlay(gps_manager=self.gps, size_hint=(1, 1))
        self.overlay.on_danger_change = self.on_danger_change
        self.overlay.on_hat_select = self.show_hat_info
        cam_box.add_widget(self.overlay)

        zoom_box = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=50,
            padding=8,
            spacing=8
        )
        zoom_box.add_widget(MDRaisedButton(
            text="- UZAKLAS",
            size_hint=(0.5, 1),
            md_bg_color=(0.1, 0.3, 0.6, 1),
            on_release=lambda x: self.overlay.zoom_out()
        ))
        zoom_box.add_widget(MDRaisedButton(
            text="+ YAKINLAS",
            size_hint=(0.5, 1),
            md_bg_color=(0.1, 0.3, 0.6, 1),
            on_release=lambda x: self.overlay.zoom_in()
        ))

        self.status_bar = MDLabel(
            text="  GPS bekleniyor...",
            halign="left",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.5, 1, 0.5, 1),
            size_hint=(1, None),
            height=28
        )

        root.add_widget(toolbar)
        root.add_widget(cam_box)
        root.add_widget(zoom_box)
        root.add_widget(self.status_bar)
        self.add_widget(root)

        Clock.schedule_interval(self.update_status, 1)

    def update_status(self, dt):
        lat, lon, acc = self.gps.get_location()
        self.status_bar.text = f"  GPS: {lat:.5f}, {lon:.5f}  |  Dogruluk: {acc:.0f}m"

    def on_danger_change(self, danger, hat):
        if danger and hat:
            self.status_bar.text = f"  !! TEHLIKE: {hat['type']} — {hat['company']} !!"
            self.status_bar.text_color = (1, 0.1, 0.1, 1)
        else:
            lat, lon, acc = self.gps.get_location()
            self.status_bar.text = f"  GPS: {lat:.5f}, {lon:.5f}  |  Dogruluk: {acc:.0f}m"
            self.status_bar.text_color = (0.5, 1, 0.5, 1)

    def show_hat_info(self, hat):
        if self.dialog:
            self.dialog.dismiss()

        extras = []
        for key, label in [("pressure", "Basinc"), ("voltage", "Gerilim"),
                            ("bandwidth", "Bant Genisligi"), ("depth_cm", "Derinlik (cm)")]:
            if key in hat:
                extras.append(f"{label}: {hat[key]}")

        my_lat, my_lon, _ = self.gps.get_location()
        coords = hat.get("coordinates", [])
        min_dist = None
        if coords:
            dists = [haversine_distance(my_lat, my_lon, c["lat"], c["lon"]) for c in coords]
            min_dist = min(dists)

        dist_text = f"Konumunuza uzaklik: {min_dist:.1f} m\n" if min_dist else ""

        self.dialog = MDDialog(
            title=f"{hat['type']}  —  {hat.get('name', '')}",
            text=(
                f"Firma: {hat.get('company', '—')}\n"
                f"Yil: {hat.get('year', '—')}\n"
                f"{chr(10).join(extras)}\n"
                f"{dist_text}"
            ),
            buttons=[
                MDFlatButton(text="KAPAT", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()


# ─────────────────────────────────────────
#  EKRAN 2 – VERİTABANI
# ─────────────────────────────────────────

class DBScreen(MDScreen):
    def __init__(self, ar_screen, **kwargs):
        super().__init__(**kwargs)
        self.name = "db"
        self.ar_screen = ar_screen

        root = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title="VERITABANI",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, "current", "ar")]]
        )

        layout = MDBoxLayout(orientation="vertical", padding=20, spacing=14)

        lbl = MDLabel(
            text="JSON dosyasindan yukle veya API'den cek",
            halign="center",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=50
        )

        self.api_field = MDTextField(
            hint_text="API URL girin",
            mode="rectangle",
            size_hint_y=None,
            height=52
        )

        layout.add_widget(lbl)
        layout.add_widget(self.api_field)

        for text, color, fn in [
            ("API'DEN CEK", (0.1, 0.5, 0.9, 1), self.fetch_api),
            ("JSON DOSYASINDAN YUKLE", (0.1, 0.6, 0.3, 1), self.load_json),
            ("VARSAYILAN VERILERI YUKLE", (0.4, 0.2, 0.6, 1), self.load_defaults),
        ]:
            layout.add_widget(MDRaisedButton(
                text=text,
                pos_hint={"center_x": 0.5},
                md_bg_color=color,
                on_release=fn
            ))

        self.result_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        layout.add_widget(self.result_label)
        root.add_widget(toolbar)
        root.add_widget(layout)
        self.add_widget(root)

    def fetch_api(self, instance):
        url = self.api_field.text.strip()
        if not url:
            self.result_label.text = "API URL giriniz!"
            return
        self.result_label.text = "Cekiliyor..."
        threading.Thread(target=self._do_fetch, args=(url,), daemon=True).start()

    def _do_fetch(self, url):
        data = fetch_hatlar_from_api(url)
        if data:
            save_hatlar(data)
            self.ar_screen.overlay.reload_hatlar()
            Clock.schedule_once(lambda dt: setattr(
                self.result_label, "text", f"Basarili! {len(data)} hat yuklendi."), 0)
        else:
            Clock.schedule_once(lambda dt: setattr(
                self.result_label, "text", "API hatasi!"), 0)

    def load_json(self, instance):
        data = load_hatlar()
        self.ar_screen.overlay.reload_hatlar()
        self.result_label.text = f"JSON'dan {len(data)} hat yuklendi."

    def load_defaults(self, instance):
        save_hatlar(DEFAULT_HATLAR)
        self.ar_screen.overlay.reload_hatlar()
        self.result_label.text = f"Varsayilan {len(DEFAULT_HATLAR)} hat yuklendi."


# ─────────────────────────────────────────
#  EKRAN 3 – HAT LİSTESİ
# ─────────────────────────────────────────

class ListScreen(MDScreen):
    def __init__(self, gps_manager, **kwargs):
        super().__init__(**kwargs)
        self.name = "list"
        self.gps = gps_manager

        root = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title="ALTYAPI HATLARI",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, "current", "ar")]]
        )

        self.layout = MDBoxLayout(orientation="vertical", padding=20, spacing=10)
        root.add_widget(toolbar)
        root.add_widget(self.layout)
        self.add_widget(root)
        self.bind(on_pre_enter=self.refresh)

    def refresh(self, *args):
        self.layout.clear_widgets()
        hatlar = load_hatlar()
        my_lat, my_lon, _ = self.gps.get_location()

        for hat in hatlar:
            coords = hat.get("coordinates", [])
            dists = [haversine_distance(my_lat, my_lon, c["lat"], c["lon"]) for c in coords]
            min_dist = min(dists) if dists else 0
            r, g, b, a = hat["color"]

            self.layout.add_widget(MDLabel(
                text=(
                    f"[b]{hat['type']}[/b]  —  {hat.get('company', '—')}\n"
                    f"Derinlik: {hat.get('depth_cm','—')} cm  |  Uzaklik: {min_dist:.0f} m"
                ),
                markup=True,
                halign="left",
                font_style="Body2",
                theme_text_color="Custom",
                text_color=(r, g, b, 1),
                size_hint_y=None,
                height=56
            ))


# ─────────────────────────────────────────
#  EKRAN 4 – HAKKINDA
# ─────────────────────────────────────────

class InfoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "info"

        root = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title="HAKKINDA",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, "current", "ar")]]
        )

        layout = MDBoxLayout(orientation="vertical", padding=30, spacing=10)
        layout.add_widget(MDLabel(
            text=(
                f"[b]KOSTEBEK-AR[/b]\n"
                f"Surum: {APP_VERSION}\n\n"
                "Gelistirici: FRT Design\n\n"
                "GPS tabanli AR altyapi gorselleştirme.\n"
                "Yeralti hatlarini gercek zamanli haritalar.\n\n"
                "[b]Desteklenen Hatlar:[/b]\n"
                "Dogalgaz / Su / Elektrik / Fiber Optik\n\n"
                "[b]Yakinda:[/b]\n"
                "PDF rapor / QR kod / Ariza kayit\n\n"
                "c 2026 FRT Design"
            ),
            markup=True,
            halign="center",
            font_style="Body2",
            theme_text_color="Secondary"
        ))
        root.add_widget(toolbar)
        root.add_widget(layout)
        self.add_widget(root)


# ─────────────────────────────────────────
#  ANA UYGULAMA
# ─────────────────────────────────────────

class KostebekARApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        Window.clearcolor = (0.03, 0.03, 0.03, 1)

        self.gps = GPSManager()
        sm = MDScreenManager()
        ar = ARScreen(gps_manager=self.gps)
        db = DBScreen(ar_screen=ar)
        sm.add_widget(ar)
        sm.add_widget(db)
        sm.add_widget(ListScreen(gps_manager=self.gps))
        sm.add_widget(InfoScreen())
        return sm

    def on_stop(self):
        self.gps.stop()


if __name__ == "__main__":
    KostebekARApp().run()
