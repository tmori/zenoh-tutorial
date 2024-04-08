#!/bin/bash

if [ -d cmake-build ]
then
	:
else
	mkdir cmake-build
fi
cd cmake-build
cmake  -DCMAKE_PREFIX_PATH=../../../build/install ..
make
