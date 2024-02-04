#!/bin/bash

mode=$1

if [ "$mode" = "development" ]; then
    echo "Running in development mode"
    gunicorn --bind :8050 --log-level info --workers 1 --threads 8 --timeout 0 --reload app:server
else
    gunicorn --bind :8050 --log-level info --workers 1 --threads 8 --timeout 0 app:server
fi