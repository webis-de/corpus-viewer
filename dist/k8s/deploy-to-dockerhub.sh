#!/bin/bash -e

docker login

cd dist/docker/
./build.sh
cd ..

docker push webis/corpus-viewer-base:1.0.2


