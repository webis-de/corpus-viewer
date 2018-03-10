1. run the follwoing command to build the image `./build.sh`

2. create a `<name>.conf` file which defines the following settings for one corpus:
```
#mandatory
file_settings="<path/to/settingsfile>" #if relative, relative to the run.sh!
data_output="<path/to/dataouput>" #if relative, relative to the run.sh!
port="<port>"

#optional
name_container="<name>"
data_corpus="<path/to/corpusdata>" #if relative, relative to the run.sh!
```
3. pass the path(s) to the configfile(s) to the run.sh:
`./run.sh ./*.conf` or `./run.sh ./conf/someconfig.conf` or ... 

<!-- 2. run the follwoing command to spawn a container
`./run.sh -s settings_netspeak.py -d ./ -p 4000 -o docker_output`
 
3. visit `localhost:4000/netspeak` -->

4. Stop and remove a container by running `docker stop <container> && docker rm <container>` or stop and remove all containers by running `sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q)`
