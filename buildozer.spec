[app]
title = MyApp
package.name = myapp
package.domain = org.myapp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.2

requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,hostpython3,libffi,openssl,certifi

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
p4a.branch = develop
