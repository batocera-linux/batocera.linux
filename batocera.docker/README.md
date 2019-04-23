# Install docker
  **Ubuntu:** https://docs.docker.com/install/linux/docker-ce/ubuntu/

  **Fedora:** https://docs.docker.com/install/linux/docker-ce/fedora/

  **Windows:** https://docs.docker.com/docker-for-windows/install/

# Create the batocera docker image on your computer
```
sudo docker build -t batocera-docker .
```
# Start the container and compile
```
cd [Where you want] # which contains the batocera.linux directory
sudo docker run -it --rm -v $PWD/batocera.linux:/build batocera-docker
cat /etc/lsb-release # Ubuntu 18.04
make batocera-rpi3_defconfig
make
ls output/images/batocera
exit # exit from the docker, your files are still here in $PWD/batocera.linux
```
to return in the docker and continue to work
```
sudo docker run -it --rm -v $PWD/batocera.linux:/build batocera-docker
```
# Tips
###### List docker images
```
sudo docker image ls
```
###### Remove docker images
```
sudo docker rmi [image]
```
###### List docker containers
```
sudo docker ps
```
###### Remove docker containers
```
sudo docker kill [container name]
```
###### Build the image from a docker file
```
cd batocera.docker
sudo docker build . -t batocera-docker
```

*Credits: http://batocera-linux.xorhub.com/wiki/doku.php?id=en:compile_batocera.linux_via_docker*
