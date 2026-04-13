[app]
title = KOSTEBEK-AR
package.name = kostebekar
package.domain = org.frtdesign

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 2026.04.13

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,plyer,sqlite3

orientation = portrait

fullscreen = 0

android.permissions = INTERNET, CAMERA, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, POST_NOTIFICATIONS, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.enable_androidx = True

p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
