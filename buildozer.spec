[app]
title = FRT Design App
package.name = frtdesign
package.domain = org.frt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Burası en önemli yer, bilgisayara hangi malzemeleri kullanacağını söylüyoruz
requirements = python3,kivy,hostpython3,libffi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Android telefonun anlayacağı dil ayarları
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

[buildozer]
log_level = 2
warn_on_root = 1
