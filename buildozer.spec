# This .spec config file tells Buildozer an app's requirements for being built.
# Optimized specifically for the Study Focus Music Player.

[app]

# (str) Title of your application
title = Study Focus

# (str) Package name
package.name = studyfocus

# (str) Package domain (needed for android/ios packaging)
package.domain = org.studybeats

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0

# (list) Application requirements
# අන්තර්ජාලයෙන් සුරක්ෂිතව (HTTPS) සංගීතය ලබා ගැනීමට openssl, requests, සහ certifi එක් කර ඇත.
requirements = python3, kivy, openssl, requests, certifi

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# INTERNET: අන්තර්ජාලයෙන් සිංදු ප්ලේ කිරීමට.
# WAKE_LOCK: දුරකථනය ලොක් කර ඇති විට සංගීතය නතර වීම වැළැක්වීමට.
android.permissions = android.permission.INTERNET, android.permission.WAKE_LOCK

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (bool) Indicate whether the screen should stay on (or continue audio playback)
android.wakelock = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1