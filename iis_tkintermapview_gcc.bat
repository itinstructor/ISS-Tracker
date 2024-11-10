cd c:\temp

python -m nuitka ^
    --onefile ^
    --mingw64 ^
    --lto=no ^
    --plugin-enable=tk-inter ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=map.ico ^
    iss_tkintermapview.py
pause
