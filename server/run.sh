#!/bin/bash
. ./venv/bin/activate
if [ $# -gt 0 ]; then
    cmd="$1"
    shift
    PYTHONPATH=. django-admin "$cmd" --settings server.settings $@
else
    PYTHONPATH=. django-admin runserver --settings server.settings  0.0.0.0:8000
fi
