@echo off
cd /d "%~dp0"
py -m flask --app backend.app run --host 127.0.0.1 --port 5500 --debug
