#!/usr/bin/env bash

python3 -m PyInstaller -F --hidden-import PIL._tkinter_finder main.py