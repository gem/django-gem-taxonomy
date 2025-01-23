#!/bin/bash
. ./venv/bin/activate
PYTHONPATH=. django-admin runserver --settings server.settings  0.0.0.0:8000
