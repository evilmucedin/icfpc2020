#!/bin/sh
cd build
./app "$@" || echo "run error code: $?"
