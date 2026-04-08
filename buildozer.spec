[app]
title = FRT Design App
package.name = frtdesign
package.domain = org.frt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Burayı güncelledim, hata veren kısmı atlamasına yardımcı olacak
requirements = python3,kivy==2.2.1,hostpython3,libffi,openssl

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True

# En stabil versiyonları seçtim
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

[buildozer]
log_level = 2
warn_on_root = 1
