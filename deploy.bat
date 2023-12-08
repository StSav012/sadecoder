python -m nuitka ^
 --onefile ^
 --deployment ^
 --windows-icon-from-ico=icon.png ^
 --disable-console ^
 --enable-plugin=tk-inter ^
 --nofollow-import-to=email ^
 --nofollow-import-to=decimal ^
 --nofollow-import-to=hashlib ^
 --nofollow-import-to=bz2 ^
 --nofollow-import-to=lzma ^
 --nofollow-import-to=select ^
 --output-filename=sadecoder ^
 main.py
