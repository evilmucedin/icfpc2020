#!/bin/sh
# cd build
# ./app "$@" || echo "run error code: $?"
python src/python_eval/app.py "$@" || echo "run error code: $?"
