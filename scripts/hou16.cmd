@echo off
setlocal
set SRCPATH=%~dp0
set STARTER=wrapHou.py
set VERSION=16.0.557
set SCENE=%1

python %SRCPATH%%STARTER% %VERSION% %SCENE%