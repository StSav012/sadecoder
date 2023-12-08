/bin/env python -m nuitka \
 --onefile \
 --deployment \
 --macos-create-app-bundle --macos-app-icon=icon.png \
 --disable-console \
 --enable-plugin=tk-inter \
 --nofollow-import-to=email \
 --nofollow-import-to=decimal \
 --nofollow-import-to=hashlib \
 --nofollow-import-to=bz2 \
 --nofollow-import-to=lzma \
 --nofollow-import-to=select \
 --nofollow-import-to=csv \
 --nofollow-import-to=statictics \
 --output-filename=sadecoder \
 main.py
