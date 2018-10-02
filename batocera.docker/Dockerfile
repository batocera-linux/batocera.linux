FROM ubuntu:18.04

RUN dpkg --add-architecture i386 && apt update && apt install -y libc6:i386 libncurses5:i386 libstdc++6:i386 build-essential git libncurses5-dev libssl-dev mercurial texinfo zip default-jre imagemagick subversion autoconf automake bison scons libglib2.0-dev bc mtools u-boot-tools flex wget cpio dosfstools libtool rsync device-tree-compiler && apt clean

# device-tree-compiler : required for device-trees-aml-s9xx
# libc6:i386 libncurses5:i386 libstdc++6:i386: required for mame2016

RUN mkdir -p /build
WORKDIR /build

CMD ["/bin/bash"]
