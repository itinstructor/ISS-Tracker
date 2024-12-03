cd c:\temp

python -m nuitka ^
    --onefile ^
    --mingw64 ^
    --lto=no ^
    --plugin-enable=tk-inter ^
    --nofollow-import-to=PySide6 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=./img/map.ico ^
    iss_tracker.py
pause
