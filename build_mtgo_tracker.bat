pyinstaller -w --onefile -i "icon.ico" --hidden-import "babel.numbers" mtgo_tracker.py
rmdir build /s /q
del mtgo_tracker.spec
cd dist
mkdir save
mkdir gamelogs
mkdir draftlogs
mkdir export
cd ..
copy icon.ico dist\icon.ico
copy INPUT_OPTIONS.txt dist\INPUT_OPTIONS.txt
copy MULTIFACED_CARDS.txt dist\MULTIFACED_CARDS.txt
copy ALL_DECKS dist\ALL_DECKS
cd dist
:: update version number.
"C:\Program Files\WinRAR\rar" a -r "..\MTGO-Tracker-v.15.rar"
cd ..
rmdir dist /s /q