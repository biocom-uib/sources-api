#!/bin/sh

/usr/local/bin/gunicorn api.server:app \
    --chdir=/opt \
    -w 1 \
    -b 0.0.0.0:8080 \
    -n api \
    --worker-class aiohttp.GunicornUVLoopWebWorker \
    --reload \
    --access-logfile "-" \
    --access-logformat '%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i" %Tf' \
    --timeout 3600
    --graceful-timeout 3600
