[app]
title = Snake Mobile
package.name = snakemobile
package.domain = org.omarpro

# (str) Source files where the let's go
source.dir = .

# (list) Source files to include (let it specify extensions)
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,pygame
orientation = portrait
fullscreen = 1
android.permissions = 
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
