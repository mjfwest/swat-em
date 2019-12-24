Rem  Do not forget to define the version number in the pack.nsi file


del /s /q swat-em
rmdir /s /q swat-em

del /s /q dist
rmdir /s /q dist
del SWAT-EM_portable.zip
del SWAT-EM_Setup.exe

git clone https://gitlab.com/martinbaun/swat-em.git
pyinstaller swat-em\swat_em\main.py --name swat-em --noconsole  --exclude scipy --exclude matplotlib --icon=swat-em\swat_em\ui\icons\app_icon.ico
xcopy /e /v swat-em\swat_em\ui .\dist\swat-em\ui\
xcopy /e /v swat-em\swat_em\doc .\dist\swat-em\doc\

"C:\Program Files (x86)\NSIS\makensisw.exe" pack.nsi


cd /D dist
"C:\Program Files (x86)\7-Zip\7zG.exe" a SWAT-EM_portable.zip swat-em\
move SWAT-EM_portable.zip ..\
