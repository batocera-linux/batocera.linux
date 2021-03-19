FROM ubuntu:20.10
ARG DEBIAN_FRONTEND=noninteractive
RUN dpkg --add-architecture i386 && \
	apt update && \
	apt install -y -o APT::Immediate-Configure=0 libc6:i386 \
		libncurses6:i386 \
		libstdc++6:i386 \
		build-essential \
		git \
		libncurses6 \
		libncurses-dev \
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
		graphviz \
		python \
		gcc-multilib \
		g++-multilib \
	&& apt clean

# Set locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
	locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV TZ Europe/Paris

# Workaround host-tar configure error
ENV FORCE_UNSAFE_CONFIGURE 1

# device-tree-compiler : required for device-trees-aml-s9xx
# libc6:i386 libncurses5:i386 libstdc++6:i386: required for mame2016
# gettext : required for buildstats.sh

RUN mkdir -p /build
WORKDIR /build

CMD ["/bin/bash"]
