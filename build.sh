#!/bin/sh
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j 8
cp ../release/build/app.exe .
# cd src/app
# mkdir -p ../../build
# g++ -std=c++11 -o ../../build/main main.cpp
