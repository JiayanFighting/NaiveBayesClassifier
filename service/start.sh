#!/bin/bash


cd /web_service/spam_checker
## old uwsgi
#uwsgi --http-socket :9002 --master --workers 3 --uid nobody  --wsgi-file  hello.py  --callable app
gunicorn --backlog 1024 -w 1 -b 0.0.0.0:9006  main:app \
    --log-level error --access-logfile ./logs/gunicorn_access.log --error-logfile ./logs/gunicorn_error.log \
    --access-logformat '%(h)s [%({X-Forwarded-For}i)s] %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%(L)s"'  \
    --user developer --pid gunicorn.pid
