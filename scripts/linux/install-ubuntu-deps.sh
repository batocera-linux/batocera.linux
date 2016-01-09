#!/bin/bash -e

if [ "$USER" != "root" ]; then
    echo "This script must be runned as root user."
    exit 1
fi

echo "Installing / updating ubuntu dependencies..."
apt-get install \
    build-essential \
    git \
    libncurses5-dev \
    qt5-default \
    qttools5-dev-tools \
    mercurial \
    libdbus-glib-1-dev \
    texinfo \
    zip \
    openjdk-8-jdk \
    inotify-tools \
    graphicsmagick-imagemagick-compat
