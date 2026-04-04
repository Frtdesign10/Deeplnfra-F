[app]
title = Frt Design App
package.name = frtdesign
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

# Building only for arm64-v8a saves massive time and prevents crashes
android.archs = arm64-v8a

# Mandatory for GitHub Actions
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
