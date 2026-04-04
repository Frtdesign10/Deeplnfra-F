[app]
# (str) Uygulama başlığı
title = My Kivy App

# (str) Paket adı
package.name = frtdesignapp

# (str) Paket domaini
package.domain = org.frtdesign

# (str) Ana dosya konumu
source.dir = .

# (list) Dahil edilecek dosyalar (uzantılara dikkat)
source.include_exts = py,png,jpg,kv,atlas

# (str) Uygulama versiyonu
version = 0.1

# (list) Uygulama gereksinimleri (Kivy sürümü belirtmeye gerek yok, en günceli çeker)
requirements = python3,kivy

# (str) Desteklenen ekran yönü
orientation = portrait

# (bool) Tam ekran modu
fullscreen = 0

# (list) Android izinleri
android.permissions = INTERNET

# (int) Android API seviyesi (33 veya 34 önerilir)
android.api = 33

# (int) Minimum API seviyesi
android.minapi = 21

# (str) Android NDK sürümü (Genellikle otomatik seçilir ama gerekirse belirtilir)
# android.ndk = 25b

# (list) Desteklenen mimariler (Actions için ikisini de eklemek iyidir)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Kalıntıları temizle (GitHub Actions'ta True olması iyidir)
warn_on_root = 1

[buildozer]
# (int) Log seviyesi (Hata ayıklama için 2 kalsın)
log_level = 2

# (int) Çıktı klasörü (YAML dosyanla uyumlu olmalı)
bin_dir = ./bin
