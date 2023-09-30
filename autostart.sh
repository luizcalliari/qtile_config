#!/bin/bash
xrandr --output HDMI-1 --primary #--mode 1920x1080
xrandr --output HDMI-2 --rotate left --mode 1920x1080
xset s off
xset -dpms
