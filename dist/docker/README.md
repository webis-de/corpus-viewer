1. run the follwoing command to build the image `./build.sh`

2. run the follwoing command to spawn a container
`./run.sh -s settings_netspeak.py -d ./ -p 4000 -o docker_output`
 
3. visit `localhost:4000/netspeak`

4. Stop and remove a container by running `docker stop <container> && docker rm <container>` or stop and remove all containers by running `sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q)`
