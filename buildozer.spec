[app]
title = FrtApp
package.name = frtapp
package.domain = org.frt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
