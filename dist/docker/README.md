1. run the follwoing command to build the image
./build.sh

2. run the follwoing command to spawn a container (replace '<path-to>')
./run.sh -s <path-to>/corpus-viewer/dist/docker/settings_netspeak.py -d <path-to>/corpus-viewer/dist/docker/ -p 4000 -o <path-to>/corpus-viewer/dist/docker/docker_output
 
3. visit localhost:4000/netspeak