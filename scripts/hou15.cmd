@echo off
setlocal
set SRCPATH=%~dp0
set STARTER=wrapHou.py
set VERSION=15.5.480
set SCENE=%1

python %SRCPATH%%STARTER% %VERSION% %SCENE%