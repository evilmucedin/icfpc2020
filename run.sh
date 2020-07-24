#!/bin/sh
cd build
./app2 "$@" || echo "run error code: $?"
# python src/python_eval/app.py "$@" || echo "run error code: $?"
