@echo off
taskkill /F /PID 45696
taskkill /F /PID 88096
timeout /t 2
netstat -ano | findstr ":10181"
