FROM ubuntu:18.04

RUN dpkg --add-architecture i386 && \
	apt update && \
	apt install -y libc6:i386 \
		libncurses5:i386 \
		libstdc++6:i386 \
		build-essential \
		git \
		libncurses5-dev \
		libssl-dev \
		mercurial \
		texinfo \
		zip \
		default-jre \
		imagemagick \
		subversion \
		autoconf \
		automake \
		bison \
		scons \
		libglib2.0-dev \
		bc \
		mtools \
		u-boot-tools \
		flex \
		wget \
		cpio \
		dosfstools \
		libtool \
		rsync \
		device-tree-compiler \
		gettext \
		locales \
	&& apt clean

# Set locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
	locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Workaround host-tar configure error
ENV FORCE_UNSAFE_CONFIGURE 1

# device-tree-compiler : required for device-trees-aml-s9xx
# libc6:i386 libncurses5:i386 libstdc++6:i386: required for mame2016
# gettext : required for buildstats.sh

RUN mkdir -p /build
WORKDIR /build

CMD ["/bin/bash"]
