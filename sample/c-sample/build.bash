#!/bin/bash

if [ -d cmake-build ]
then
	:
else
	mkdir cmake-build
fi
cd cmake-build

cmake -DZENOH_C_LIBRARY=../../../zenoh-c-install/lib/libzenohc.so ..
make
