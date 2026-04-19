APP_VERSION = "2026.04.19"

import json, os, math, threading, time
from datetime import datetime

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock

Window.clearcolor = (0.03, 0.03, 0.03, 1)

# ─────────────────────────────────────────
#  USERS & DATA
# ─────────────────────────────────────────

USERS = {"admin": "1234", "frtdesign": "kostebek"}

DEFAULT_LINES = [
    {"id":1,"name":"Main Gas Line","type":"GAS","company":"IGDAS",
     "depth_cm":150,"pressure":"4 bar","year":2008,"danger_radius":50,
     "coordinates":[{"lat":41.01500,"lon":28.97900},{"lat":41.01500,"lon":28.98200}],
     "color":[0,1,1,0.85],"thickness":8},
    {"id":2,"name":"Water Line","type":"WATER","company":"ISKI",
     "depth_cm":80,"pressure":"2.5 bar","year":2015,"danger_radius":30,
     "coordinates":[{"lat":41.01480,"lon":28.98050},{"lat":41.01550,"lon":28.98050}],
     "color":[0.2,0.5,1,0.85],"thickness":6},
    {"id":3,"name":"Electric Line","type":"ELECTRIC","company":"BEDAS",
     "depth_cm":60,"voltage":"380V","year":2012,"danger_radius":40,
     "coordinates":[{"lat":41.01460,"lon":28.97950},{"lat":41.01460,"lon":28.98150}],
     "color":[1,0.85,0,0.85],"thickness":5},
    {"id":4,"name":"Fiber Optic","type":"FIBER","company":"TURK TELEKOM",
     "depth_cm":40,"bandwidth":"10Gbps","year":2019,"danger_radius":20,
     "coordinates":[{"lat":41.01510,"lon":28.97920},{"lat":41.01510,"lon":28.98180}],
     "color":[0.4,1,0.4,0.85],"thickness":4},
]

DB_PATH       = "/sdcard/kostebek_lines.json"
FAULTS_PATH   = "/sdcard/kostebek_faults.json"
API_CFG_PATH  = "/sdcard/kostebek_api.json"
PHOTOS_DIR    = "/sdcard/kostebek_photos/"

def load_lines():
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH) as f:
                d = json.load(f)
                if d: return d
    except: pass
    return list(DEFAULT_LINES)

def save_lines(lines):
    try:
        with open(DB_PATH,"w") as f: json.dump(lines, f, indent=2)
    except: pass

def load_faults():
    try:
        if os.path.exists(FAULTS_PATH):
            with open(FAULTS_PATH) as f: return json.load(f)
    except: pass
    return []

def save_fault(fault):
    faults = load_faults()
    faults.append(fault)
    try:
        with open(FAULTS_PATH,"w") as f: json.dump(faults, f, indent=2)
    except: pass

def load_api_config():
    try:
        if os.path.exists(API_CFG_PATH):
            with open(API_CFG_PATH) as f: return json.load(f)
    except: pass
    return {"url": "", "key": ""}

def save_api_config(cfg):
    try:
        with open(API_CFG_PATH,"w") as f: json.dump(cfg, f)
    except: pass

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin(math.radians(lat2-lat1)/2)**2 + \
        math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def gps_to_px(lat, lon, my_lat, my_lon, w, h, scale=50000):
    dx = (lon-my_lon)*111320*math.cos(math.radians(my_lat))
    dy = (lat-my_lat)*111320
    return w/2+dx*(scale/111320), h/2-dy*(scale/111320)

def line_dist(p1, p2, pt):
    x1,y1=p1; x2,y2=p2; px,py=pt
    dx,dy=x2-x1,y2-y1
    if dx==0 and dy==0: return math.hypot(px-x1,py-y1)
    t = max(0,min(1,((px-x1)*dx+(py-y1)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def get_nearby(lat, lon, max_dist=200):
    result = []
    for ln in load_lines():
        coords = ln.get("coordinates",[])
        dists = [haversine(lat,lon,c["lat"],c["lon"]) for c in coords]
        if dists:
            result.append({"line":ln,"distance":min(dists)})
    return sorted(result, key=lambda x: x["distance"])

# ─────────────────────────────────────────
#  PDF
# ─────────────────────────────────────────

def generate_pdf(lat, lon, nearby, path):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors as rcolors

        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("KOSTEBEK-AR  EXCAVATION SAFETY REPORT", styles['Title']))
        story.append(Spacer(1,10))
        story.append(Paragraph(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Paragraph(f"Location: {lat:.6f}, {lon:.6f}", styles['Normal']))
        story.append(Paragraph(f"Prepared by: KOSTEBEK-AR {APP_VERSION} | FRT Design", styles['Normal']))
        story.append(Spacer(1,16))
        story.append(Paragraph("UNDERGROUND INFRASTRUCTURE DETECTED:", styles['Heading2']))
        story.append(Spacer(1,6))

        if nearby:
            data = [["Type","Company","Depth(cm)","Dist(m)","Danger Zone","Safe to Dig?"]]
            for item in nearby:
                ln = item["line"]; dist = item["distance"]
                radius = ln.get("danger_radius",30)
                safe = "NO - DANGER" if dist < radius/100 else ("CAUTION" if dist < 2 else "YES")
                data.append([ln["type"], ln.get("company",""), str(ln.get("depth_cm","?")),
                              f"{dist:.1f}", f"{radius}cm", safe])
            t = Table(data, colWidths=[65,80,65,55,70,65])
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),rcolors.HexColor('#003366')),
                ('TEXTCOLOR',(0,0),(-1,0),rcolors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),8),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[rcolors.lightgrey,rcolors.white]),
                ('GRID',(0,0),(-1,-1),0.3,rcolors.grey),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("No underground infrastructure detected nearby.", styles['Normal']))

        story.append(Spacer(1,16))
        story.append(Paragraph("SAFETY RULES:", styles['Heading2']))
        for r in [
            "1. Never machine dig within danger radius - contact relevant company first.",
            "2. Hand dig only within 50cm of any underground line.",
            "3. Emergency contacts: IGDAS 187 | ISKI 185 | BEDAS 186",
            "4. This report is valid for 24 hours from generation.",
            "5. Always have a spotter when working near underground lines.",
        ]:
            story.append(Paragraph(r, styles['Normal']))

        doc.build(story)
        return True
    except Exception as e:
        print("PDF error:", e)
        return False

# ─────────────────────────────────────────
#  GPS
# ─────────────────────────────────────────

class GPSManager:
    def __init__(self):
        self.lat=41.01500; self.lon=28.98050; self.accuracy=0
        Clock.schedule_once(self._start, 2)

    def _start(self, dt):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.CAMERA,
            ])
            from plyer import gps
            self.gps=gps
            gps.configure(on_location=self._on_loc)
            gps.start(minTime=1000, minDistance=1)
        except Exception as e:
            print("GPS sim:", e)

    def _on_loc(self, **kw):
        self.lat=kw.get("lat",self.lat)
        self.lon=kw.get("lon",self.lon)
        self.accuracy=kw.get("accuracy",0)

    def get(self): return self.lat, self.lon, self.accuracy

    def stop(self):
        try: self.gps.stop()
        except: pass

# ─────────────────────────────────────────
#  AR OVERLAY
# ─────────────────────────────────────────

class AROverlay(Widget):
    def __init__(self, gps, **kw):
        super().__init__(**kw)
        self.gps=gps; self.lines=load_lines()
        self.touch_pos=(0,0); self.blink=True
        self.closest=None; self.on_danger=None; self.on_select=None
        self.scale=50000
        Clock.schedule_interval(self._tick, 0.5)
        self.bind(size=self._draw, pos=self._draw)

    def _tick(self, dt): self.blink=not self.blink; self._draw()

    def _draw(self, *a):
        self.canvas.clear()
        w,h=self.size
        if not w or not h: return
        my_lat,my_lon,_=self.gps.get()
        danger=False; closest=None; cd=9999

        with self.canvas:
            for ln in self.lines:
                coords=ln.get("coordinates",[])
                if len(coords)<2: continue
                for i in range(len(coords)-1):
                    p1=gps_to_px(coords[i]["lat"],coords[i]["lon"],my_lat,my_lon,w,h,self.scale)
                    p2=gps_to_px(coords[i+1]["lat"],coords[i+1]["lon"],my_lat,my_lon,w,h,self.scale)
                    d=line_dist(p1,p2,self.touch_pos)
                    near=d<45
                    if near:
                        danger=True
                        if d<cd: cd=d; closest=ln
                    r,g,b,a=ln["color"]; t=ln.get("thickness",5)
                    if near and self.blink:
                        Color(1,0.1,0.1,1)
                        Line(points=[p1[0],p1[1],p2[0],p2[1]],width=t*2.5)
                    else:
                        Color(r,g,b,a)
                        Line(points=[p1[0],p1[1],p2[0],p2[1]],width=t)
                    mx=(p1[0]+p2[0])/2; my2=(p1[1]+p2[1])/2
                    Color(0,0,0,0.6); Rectangle(pos=(mx-55,my2+4),size=(110,18))

            Color(0.2,0.6,1,1); Ellipse(pos=(w/2-10,h/2-10),size=(20,20))
            if danger and self.blink:
                Color(1,0,0,0.7); Line(rectangle=(3,3,w-6,h-6),width=6)

        self.closest=closest
        if self.on_danger: self.on_danger(danger,closest)

    def on_touch_move(self, touch):
        self.touch_pos=(touch.x,touch.y-self.y); self._draw(); return True

    def on_touch_down(self, touch):
        self.touch_pos=(touch.x,touch.y-self.y); self._draw()
        if self.closest and self.on_select: self.on_select(self.closest)
        return True

    def zoom_in(self): self.scale=min(self.scale*1.3,500000); self._draw()
    def zoom_out(self): self.scale=max(self.scale/1.3,5000); self._draw()
    def reload(self): self.lines=load_lines(); self._draw()

# ─────────────────────────────────────────
#  MAP OVERLAY (OSM Tiles + Lines)
# ─────────────────────────────────────────

class MapOverlay(Widget):
    def __init__(self, gps, **kw):
        super().__init__(**kw)
        self.gps=gps; self.lines=load_lines()
        self.blink=True; self.scale=50000
        self.tile_textures={}
        Clock.schedule_interval(self._tick, 0.5)
        self.bind(size=self._draw, pos=self._draw)

    def _tick(self, dt): self.blink=not self.blink; self._draw()

    def _latlon_to_tile(self, lat, lon, zoom):
        n=2**zoom
        x=int((lon+180)/360*n)
        y=int((1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n)
        return x,y

    def _fetch_tile(self, x, y, zoom):
        try:
            import urllib.request
            url=f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            path=f"/sdcard/kostebek_tiles/{zoom}_{x}_{y}.png"
            os.makedirs("/sdcard/kostebek_tiles/",exist_ok=True)
            if not os.path.exists(path):
                headers={"User-Agent":"KOSTEBEK-AR/5.0 FRTDesign"}
                req=urllib.request.Request(url,headers=headers)
                with urllib.request.urlopen(req,timeout=5) as r:
                    with open(path,"wb") as f: f.write(r.read())
            return path
        except Exception as e:
            print("Tile fetch error:",e)
            return None

    def _draw(self, *a):
        self.canvas.clear()
        w,h=self.size
        if not w or not h: return
        my_lat,my_lon,acc=self.gps.get()

        with self.canvas:
            # Background map grid
            Color(0.08,0.10,0.12,1)
            Rectangle(pos=self.pos,size=self.size)

            # Try to load OSM tile in background
            zoom=16
            tx,ty=self._latlon_to_tile(my_lat,my_lon,zoom)
            tile_key=f"{zoom}_{tx}_{ty}"

            if tile_key in self.tile_textures and self.tile_textures[tile_key]:
                from kivy.core.image import Image as CoreImage
                try:
                    tex=CoreImage(self.tile_textures[tile_key]).texture
                    Color(1,1,1,1)
                    Rectangle(pos=self.pos,size=self.size,texture=tex)
                except: pass
            else:
                # Grid placeholder while loading
                Color(0.12,0.15,0.18,1)
                for i in range(0,int(w),40):
                    Line(points=[self.x+i,self.y,self.x+i,self.y+h],width=1)
                for i in range(0,int(h),40):
                    Line(points=[self.x,self.y+i,self.x+w,self.y+i],width=1)
                if tile_key not in self.tile_textures:
                    self.tile_textures[tile_key]=None
                    threading.Thread(target=self._load_tile,
                                     args=(tx,ty,zoom,tile_key),daemon=True).start()

            # Underground lines overlay
            for ln in self.lines:
                coords=ln.get("coordinates",[])
                if len(coords)<2: continue
                for i in range(len(coords)-1):
                    p1=gps_to_px(coords[i]["lat"],coords[i]["lon"],my_lat,my_lon,w,h,self.scale)
                    p2=gps_to_px(coords[i+1]["lat"],coords[i+1]["lon"],my_lat,my_lon,w,h,self.scale)
                    p1=(p1[0]+self.x,p1[1]+self.y)
                    p2=(p2[0]+self.x,p2[1]+self.y)
                    r,g,b,a=ln["color"]
                    radius=ln.get("danger_radius",30)
                    t=ln.get("thickness",5)

                    # Danger zone (transparent band)
                    Color(r,g,b,0.12)
                    Line(points=[p1[0],p1[1],p2[0],p2[1]],width=radius*0.3)

                    # Main line
                    Color(r,g,b,0.9)
                    Line(points=[p1[0],p1[1],p2[0],p2[1]],width=t)

                    # Depth label
                    mx=(p1[0]+p2[0])/2; my2=(p1[1]+p2[1])/2
                    Color(0,0,0,0.7)
                    Rectangle(pos=(mx-60,my2+4),size=(120,20))

            # User position
            cx=self.x+w/2; cy=self.y+h/2
            if acc>0:
                ap=max(acc*0.3,15)
                Color(0.2,0.6,1,0.15)
                Ellipse(pos=(cx-ap,cy-ap),size=(ap*2,ap*2))
            Color(0.2,0.6,1,1); Ellipse(pos=(cx-10,cy-10),size=(20,20))
            Color(1,1,1,1);     Ellipse(pos=(cx-4,cy-4),size=(8,8))

            # Compass
            Color(1,0.3,0.3,0.8)
            Line(points=[cx,cy+12,cx,cy+24],width=2)

    def _load_tile(self, tx, ty, zoom, key):
        path=self._fetch_tile(tx,ty,zoom)
        if path:
            self.tile_textures[key]=path
            Clock.schedule_once(lambda dt: self._draw(), 0)

    def reload(self): self.lines=load_lines(); self._draw()
    def zoom_in(self): self.scale=min(self.scale*1.3,500000); self._draw()
    def zoom_out(self): self.scale=max(self.scale/1.3,5000); self._draw()

# ─────────────────────────────────────────
#  SCREEN: LOGIN
# ─────────────────────────────────────────

class LoginScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name="login"
        root=MDBoxLayout(orientation="vertical",padding=40,spacing=16)
        root.add_widget(MDLabel(text="KOSTEBEK-AR",halign="center",font_style="H4",
            theme_text_color="Custom",text_color=(0,0.8,1,1)))
        root.add_widget(MDLabel(text="Underground Infrastructure AR System",
            halign="center",font_style="Caption",theme_text_color="Secondary"))
        root.add_widget(MDLabel(text=f"v{APP_VERSION}  |  FRT Design",halign="center",
            font_style="Caption",theme_text_color="Hint"))
        self.user_f=MDTextField(hint_text="Username",mode="rectangle",
            size_hint_y=None,height=52)
        self.pass_f=MDTextField(hint_text="Password",mode="rectangle",
            password=True,size_hint_y=None,height=52)
        self.msg=MDLabel(text="",halign="center",font_style="Caption",
            theme_text_color="Custom",text_color=(1,0.3,0.3,1),
            size_hint_y=None,height=28)
        root.add_widget(self.user_f); root.add_widget(self.pass_f)
        root.add_widget(self.msg)
        root.add_widget(MDRaisedButton(text="LOGIN",pos_hint={"center_x":0.5},
            md_bg_color=(0,0.5,1,1),size_hint=(0.6,None),height=48,
            on_release=self._login))
        root.add_widget(MDFlatButton(text="Demo Mode",pos_hint={"center_x":0.5},
            on_release=lambda x: setattr(self.manager,"current","ar")))
        self.add_widget(root)

    def _login(self, *a):
        u=self.user_f.text.strip(); p=self.pass_f.text.strip()
        if USERS.get(u)==p: self.msg.text=""; self.manager.current="ar"
        else: self.msg.text="Invalid username or password!"

# ─────────────────────────────────────────
#  SCREEN: AR
# ─────────────────────────────────────────

class ARScreen(MDScreen):
    def __init__(self, gps, **kw):
        super().__init__(**kw)
        self.name="ar"; self.gps=gps
        root=MDBoxLayout(orientation="vertical")

        top=MDBoxLayout(size_hint=(1,None),height=48,padding=3,spacing=3)
        top.add_widget(MDLabel(text=f"AR {APP_VERSION}",font_style="Caption",
            theme_text_color="Custom",text_color=(0,0.8,1,1)))
        for txt,dest,col in [
            ("MAP","map",(0.1,0.4,0.2,1)),
            ("LIST","list",(0.1,0.3,0.5,1)),
            ("FAULT","fault",(0.5,0.1,0.1,1)),
            ("PDF","pdf",(0.3,0.1,0.5,1)),
            ("QR","qr",(0.1,0.3,0.3,1)),
            ("API","apicfg",(0.3,0.3,0.1,1)),
        ]:
            top.add_widget(MDRaisedButton(text=txt,size_hint=(None,None),
                size=("46dp","36dp"),md_bg_color=col,
                on_release=lambda x,d=dest: setattr(self.manager,"current",d)))

        cam_box=MDBoxLayout()
        try:
            from kivy.uix.camera import Camera
            cam=Camera(play=True,index=0,size_hint=(1,1))
            cam_box.add_widget(cam)
        except:
            cam_box.add_widget(MDLabel(text="Simulation Mode",halign="center",
                theme_text_color="Custom",text_color=(0.3,0.3,0.3,1)))

        self.overlay=AROverlay(gps=self.gps,size_hint=(1,1))
        self.overlay.on_danger=self._on_danger
        self.overlay.on_select=self._show_info
        cam_box.add_widget(self.overlay)

        zb=MDBoxLayout(size_hint=(1,None),height=44,padding=3,spacing=3)
        zb.add_widget(MDRaisedButton(text="- OUT",size_hint=(0.5,1),
            md_bg_color=(0.1,0.3,0.6,1),on_release=lambda x: self.overlay.zoom_out()))
        zb.add_widget(MDRaisedButton(text="+ IN",size_hint=(0.5,1),
            md_bg_color=(0.1,0.3,0.6,1),on_release=lambda x: self.overlay.zoom_in()))

        self.status=MDLabel(text="  Scanning...",halign="left",font_style="Caption",
            theme_text_color="Custom",text_color=(0.5,1,0.5,1),
            size_hint=(1,None),height=24)

        root.add_widget(top); root.add_widget(cam_box)
        root.add_widget(zb); root.add_widget(self.status)
        self.add_widget(root)
        Clock.schedule_interval(self._upd,1)

    def _upd(self,
