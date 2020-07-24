#!/bin/sh
mkdir -p build
cd build
rm -f ../release/build/app2.exe || true
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j 8
cp ../release/build/app2 . || true
cp ../release/build/app2.exe app2 || true
# cd src/app
# mkdir -p ../../build
# g++ -std=c++11 -o ../../build/main main.cpp
