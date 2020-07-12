#!/bin/bash



# install the necessary tool
# sudo apt install icoutils

# inkscape v0.9:
inkscape -z -w 16 -h 16 app_icon.svg -e app_icon_16.png
inkscape -z -w 32 -h 32 app_icon.svg -e app_icon_32.png
inkscape -z -w 64 -h 64 app_icon.svg -e app_icon_64.png
inkscape -z -w 128 -h 128 app_icon.svg -e app_icon_128.png
inkscape -z -w 256 -h 256 app_icon.svg -e app_icon_256.png

icotool -c -o app_icon.ico app_icon_16.png app_icon_32.png app_icon_64.png app_icon_128.png app_icon_256.png
rm app_icon_16.png app_icon_32.png app_icon_64.png app_icon_128.png app_icon_256.png



# inkscape v1.0:
# inkscape -w 256 -h 256 app_icon.svg --export-filename app_icon_256.png


