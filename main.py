import cv2
import numpy as np
import math
# Başlangıç Değerleri
off_x, off_y = 0, 0
zoom = 1.0

SANAL_ALTYAPI = [
    {"p1": [50, 400], "p2": [600, 420], "type": "DOGALGAZ", "depth": 150, "color": (0, 255, 255)},
    {"p1": [320, 50], "p2": [300, 450], "type": "SU HATTI", "depth": 80, "color": (255, 0, 0)},
    {"p1": [100, 150], "p2": [500, 200], "type": "ELEKTRIK", "depth": 60, "color": (0, 0, 255)}
]

# Fare tekerleği ve konum takibi
mouse_pos = (0, 0)


def mouse_callback(event, x, y, flags, param):
    global zoom, mouse_pos
    mouse_pos = (x, y)
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            zoom += 0.05
        else:
            zoom = max(0.1, zoom - 0.05)


cap = cv2.VideoCapture(0)
cv2.namedWindow('KOSTEBEK-AR v1.3')
cv2.setMouseCallback('KOSTEBEK-AR v1.3', mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret: break
    h, w, _ = frame.shape

    danger_zone = False  # Tehlike bayrağı

    for hat in SANAL_ALTYAPI:
        # Koordinatları hesapla
        p1 = (int((hat["p1"][0] + off_x) * zoom), int((hat["p1"][1] + off_y) * zoom))
        p2 = (int((hat["p2"][0] + off_x) * zoom), int((hat["p2"][1] + off_y) * zoom))

        # Çarpışma Testi (Fare hatta ne kadar yakın?)
        # Çizgiye olan dik mesafeyi basitçe hesaplayalım
        dist = np.abs(np.cross(np.array(p2) - np.array(p1), np.array(p1) - np.array(mouse_pos))) / np.linalg.norm(
            np.array(p2) - np.array(p1))

        # Eğer fare hatta 30 birimden yakınsa uyar
        current_color = hat["color"]
        line_thickness = int(15 * zoom)

        if dist < 30:
            current_color = (0, 0, 255)  # KIRMIZIYA DÖN
            line_thickness = int(30 * zoom)  # KALINLAŞ
            danger_zone = True

        # Çizim
        overlay = frame.copy()
        cv2.line(overlay, p1, p2, current_color, line_thickness)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

        mid = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        cv2.putText(frame, f"{hat['type']}", mid, 1, 1.2, (255, 255, 255), 2)

    # TEHLİKE UYARISI
    if danger_zone:
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 10)  # Ekran kenarı kırmızı
        cv2.putText(frame, "TEHLIKE: HAT ÜZERINDESIN!", (w // 2 - 150, 50), 1, 2, (0, 0, 255), 3)

    # Kontrol Bilgileri
    cv2.putText(frame, "FARE = KEPCE UCU | W-A-S-D = HIZALA", (20, h - 20), 1, 1, (0, 255, 0), 2)
    # --- YENİ: OTOMATİK MESAFE TESPİTİ ---
    # Ekranın alt-orta kısmındaki pikselleri analiz ederek mesafe tahmini yapar
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[int(h * 0.8):h, int(w * 0.4):int(w * 0.6)]
    avg_depth = np.mean(roi)
    # Yapay zeka simülasyonu: Işık ve gölgeye göre derinlik (0-3 metre arası)
    auto_dist = round((255 - avg_depth) / 80, 2)

    # --- YENİ: DİJİTAL PUSULA ÇİZİMİ ---
    center_pc = (w - 80, 80)  # Sağ üst köşe
    cv2.circle(frame, center_pc, 50, (200, 200, 200), 2)  # Dış halka
    cv2.putText(frame, "K", (center_pc[0] - 10, center_pc[1] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Pusula iğnesi (Şimdilik sabit 45 derece, sensör bağlayınca canlı dönecek)
    angle = 45
    bx = int(center_pc[0] + 40 * math.sin(math.radians(angle)))
    by = int(center_pc[1] - 40 * math.cos(math.radians(angle)))
    cv2.line(frame, center_pc, (bx, by), (0, 0, 255), 3)

    # --- EKRAN BİLGİ PANELİ ---
    cv2.rectangle(frame, (10, h - 110), (350, h - 70), (0, 0, 0), -1)
    cv2.putText(frame, f"OTOMATIK TESPIT: {auto_dist} m", (20, h - 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    # --- 1. TEHLİKE MODU VE RENK DEĞİŞİMİ ---
    danger_limit = 0.60  # 60 cm altı tehlikeli bölge

    # Eğer otomatik tespit edilen mesafe tehlike sınırının altındaysa:
    if auto_dist < danger_limit:
        current_color = (0, 0, 255)  # Tüm hatları KIRMIZI yap
        line_thickness = 15  # Çizgileri kalınlaştır

        # Ekranın kenarlarına KIRMIZI bir çerçeve çiz (Görsel Alarm)
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 20)

        # Ekranın ortasına büyük bir uyarı yazısı
        cv2.putText(frame, "!!! DIKKAT: HAT COK YAKIN !!!", (w // 2 - 250, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    else:
        # Güvenli mesafedeyse standart renkler (Sarı/Mavi vb.)
        current_color = (0, 255, 255)  # Sarı (Doğalgaz örneği)
        line_thickness = 8
    cv2.imshow('KOSTEBEK-AR v1.3', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):
        off_y -= 10
    elif key == ord('s'):
        off_y += 10
    elif key == ord('a'):
        off_x -= 10
    elif key == ord('d'):
        off_x += 10

cap.release()
cv2.destroyAllWindows()
