@echo off
echo Starting Redis Commander...
echo.
echo Redis Commander will be available at: http://localhost:8081
echo.
echo Press Ctrl+C to stop
echo.

docker run --rm --name redis-commander ^
  -p 8081:8081 ^
  -e REDIS_HOSTS=local:host.docker.internal:6379:0:!DC1qaz2wsx ^
  ghcr.io/joeferner/redis-commander:latest
