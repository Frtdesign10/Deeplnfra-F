[app]
title = KOSTEBEK-AR
package.name = kostebekar
package.domain = org.frtdesign

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0
android.numeric_version = 1

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,plyer,reportlab,pyzbar

orientation = portrait

fullscreen = 0

android.permissions = INTERNET, CAMERA, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, POST_NOTIFICATIONS, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 30
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
