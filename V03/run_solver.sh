#!/bin/bash

nprocs=8
foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $nprocs

rm -rf 0 > /dev/null 2>&1
cp -r 0.orig 0 > /dev/null 2>&1

./include/createInitialValue.sh
setFields
decomposePar -force
mpirun -np $nprocs foamRun -parallel

