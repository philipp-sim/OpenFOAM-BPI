#!/bin/bash

nprocs=10
foamDictionary system/decomposeParDict -entry numberOfSubdomains -set $nprocs


#foamCleanTutorials
rm -rf 0 > /dev/null 2>&1
cp -r 0.orig 0 > /dev/null 2>&1


surfaceFeatures
blockMesh
decomposePar -force
mpirun -np $nprocs snappyHexMesh -parallel -overwrite 
reconstructPar -constant
createBaffles -overwrite
splitBaffles -overwrite		
#To erase empty patches
createPatch -overwrite		
splitMeshRegions -detectOnly	
renumberMesh -noFields -overwrite
#Create non-conformal couples - OF12
createNonConformalCouples -overwrite nonCouple1 nonCouple2
#createNonConformalCouples NCC1 NCC2 | tee log.createNonConformalCouples

#transformPoints 'scale = (0.01 0.01 0.01)'
checkMesh | tee log/log.checkmesh2

