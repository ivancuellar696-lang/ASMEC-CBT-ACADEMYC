[app]
title = ASMET CBT ACADEMYC
package.name = asmetcbt
package.domain = org.asmet
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,db,json
version = 3.0.0
requirements = python3, kivy==2.3.0, kivymd, pillow, requests, openssl, sqlite3, pyjnius, android
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.sdk = 27
android.ndk = 23b
android.ndk_api = 21
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.gradle_dependencies = 'com.android.support:appcompat-v7:27.1.1'

# Icono y splash (opcional, pero recomendado)
icon.filename = assets/icon.png
presplash.filename = assets/splash.png

[buildozer]
log_level = 2
warn_on_root = 1