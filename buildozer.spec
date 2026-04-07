[app]
title = FrtDesign
package.name = frtdesign
package.domain = org.frt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Kütüphaneleri sabitledik
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,plyer

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a

# GRADLE HATASINI ÇÖZEN KRİTİK SATIRLAR
android.enable_androidx = 1
android.gradle_dependencies = androidx.core:core:1.10.1
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
