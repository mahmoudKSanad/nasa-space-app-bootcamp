#!/bin/sh
if [ -n "$PORT" ]; then
  fuser -k "$PORT"/tcp
fi
source .venv/bin/activate
python mysite/manage.py runserver "$PORT"
