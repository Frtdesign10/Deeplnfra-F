[app]
title = Frt Design
package.name = frtdesign
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Gereksinimleri tam olarak böyle yap (Numpy ve OpenCV eklendi)
requirements = python3,kivy==2.2.1,opencv-python,numpy

orientation = portrait
fullscreen = 0

# İzinleri buradan kopyala (Kamera ve Dosya izni eklendi)
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
