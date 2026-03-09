#!/bin/bash

export DISPLAY=:1
export XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

Xvfb :1 -screen 0 1024x768x24 &
sleep 2

x11vnc -display :1 -forever -nopw -listen 0.0.0.0 -xkb -bg
sleep 2

/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &

while true
do
    python multi_snake.py
    sleep 1
done