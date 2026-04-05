[app]
title = FrtApp
package.name = frtapp
package.domain = org.frt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,kivymd,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
warn_on_root = 1
p4a.branch = master
[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
