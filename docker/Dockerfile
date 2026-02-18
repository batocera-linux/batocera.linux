FROM ubuntu:noble-20260113
SHELL ["/bin/bash", "-c"]

# Architecture to build for
ARG TARGETPLATFORM

ARG DEBIAN_FRONTEND=noninteractive

# This first RUN is separated from the second one because it
# shouldn't change often, and we want to cache it as much as
# possible. The second may change more often, and we don't
# want to invalidate the cache of the first one when that
# happens.
RUN <<EOF
apt-get update -y
apt-get install ca-certificates -y

echo 'APT::Snapshot "20260215T000000Z";' > /etc/apt/apt.conf.d/50snapshot

if [ "$TARGETPLATFORM" = "linux/amd64" ]; then
    dpkg --add-architecture i386
fi

apt-get update -y
apt-get upgrade -y
EOF

RUN <<EOF
PACKAGES=(
    "bc"
    "build-essential"
    "cpio"
    "curl"
    "default-jre"
    "file"
    "gettext"  # buildstats.sh
    "git"
    "gosu"  # entry-point.sh
    "graphviz"
    "libncurses6"
    "libncurses-dev"
    "libssl-dev"  # cmake build
    "locales"
    "lzip"
    "mercurial"
    "python3"
    "rsync"
    "subversion"
    "wget"
    "unzip"
)

if [ "$TARGETPLATFORM" = "linux/amd64" ]; then
    PACKAGES+=(
        "gcc-multilib"  # cross-compilation of 32-bit x86 builds on 64-bit host
        "g++-multilib"  # cross-compilation of 32-bit x86 builds on 64-bit host
        "libc6:i386"
        "libncurses6:i386"
        "libstdc++6:i386"
    )
else
    PACKAGES+=(
        "gcc-mingw-w64-x86-64-win32"  # wine
    )
fi

apt-get install -y --no-install-recommends -o APT::Immediate-Configure=0 "${PACKAGES[@]}"
apt-get clean
rm -rf /var/lib/apt/lists/*

# Set locale
sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen

# Use bash instead of dash as default shell
echo 'dash dash/sh boolean false' | debconf-set-selections
dpkg-reconfigure dash

# Create this so the ccache directory gets mounted here
mkdir -p /home/batocera
EOF

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    TZ=Europe/Paris

WORKDIR /build

COPY --chmod=0755 entry-point.sh /opt/entry-point.sh
ENTRYPOINT ["/opt/entry-point.sh"]
CMD ["/bin/bash"]
