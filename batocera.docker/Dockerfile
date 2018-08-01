FROM ubuntu:18.04

RUN apt update -y && apt -y install build-essential git libncurses5-dev libssl-dev mercurial texinfo zip default-jre imagemagick subversion autoconf automake bison scons libglib2.0-dev bc mtools u-boot-tools flex wget cpio dosfstools libtool rsync device-tree-compiler && apt clean

# device-tree-compiler : required for device-trees-aml-s9xx

RUN mkdir -p /build
WORKDIR /build

CMD ["/bin/bash"]
