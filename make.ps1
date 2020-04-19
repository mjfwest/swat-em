# Do not forget to define the version number in the pack.nsi file

Remove-Item -Recurse -Force -ErrorAction Ignore build
Remove-Item -Recurse -Force -ErrorAction Ignore dist
Remove-Item -Recurse -Force -ErrorAction Ignore SWAT-EM_portable.zip
Remove-Item -Recurse -Force -ErrorAction Ignore SWAT-EM_Setup.exe

# git clone https://gitlab.com/martinbaun/swat-em.git


git pull
.\doc\make.bat latexpdf
mkdir -Force swat_em\doc
Copy-Item "doc\build\latex\SWAT-EM.pdf" -Destination "swat_em\doc\SWAT-EM_manual.pdf"
pyinstaller swat_em\main.py --name swat-em --noconsole  --exclude scipy --exclude matplotlib --icon=swat_em\ui\icons\app_icon.ico


Copy-Item "swat_em\ui" -Recurse -Destination "dist\swat-em\ui\"
Copy-Item "swat_em\doc" -Recurse -Destination "dist\swat-em\doc\"


& "C:\Program Files (x86)\NSIS\makensisw.exe" pack.nsi

& "C:\Program Files\7-Zip\7zG.exe" a SWAT-EM_portable.zip dist\swat-em\

# clean-up
Remove-Item -Force -ErrorAction Ignore swat-em.spec

