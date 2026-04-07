[app]
title = FrtDesign
package.name = frtdesign
package.domain = org.frt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
# Pydroid'de çalışan kütüphaneler
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow
orientation = portrait
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a
android.enable_androidx = 1

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
