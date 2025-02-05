#!/bin/bash
VENV_NAME=venv_django-gem-taxonomy
if [ "$VIRTUAL_ENV" ]; then
    if [ "$(basename "$VIRTUAL_ENV")" != "$VENV_NAME" ]; then
        deactivate
        . ./$VENV_NAME/bin/activate
    fi
else
    . ./$VENV_NAME/bin/activate
fi
if [ $# -gt 0 ]; then
    cmd="$1"
    shift
    PYTHONPATH=. django-admin "$cmd" --settings server.settings $@
else
    PYTHONPATH=. django-admin runserver --settings server.settings  0.0.0.0:8000
fi
