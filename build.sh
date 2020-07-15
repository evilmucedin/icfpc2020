#!/bin/sh
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j 8
rm -f ../release/build/app.exe
cp ../release/build/app .
cp ../release/build/app.exe app
# cd src/app
# mkdir -p ../../build
# g++ -std=c++11 -o ../../build/main main.cpp
