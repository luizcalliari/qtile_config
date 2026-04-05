#!/bin/bash

#Screen configuration
xrandr --output HDMI-1 --primary
#xrandr --output HDMI-1 --mode 1920x1080
xrandr --output HDMI-1 --mode 2560x1080
#xrandr --output HDMI-2 --rotate left --mode 1920x1080
xrandr --output HDMI-0 --rotate left --mode 1920x1080

#This disables the software screensaver.
# It prevents the screen from blanking out after a period of inactivity.
xset s off
xset -dpms

#Configure keyboard
setxkbmap -layout us -variant altgr-intl
setxkbmap -layout us -variant intl

#Create wallpaper folder
mkdir ~/wallpaper/
