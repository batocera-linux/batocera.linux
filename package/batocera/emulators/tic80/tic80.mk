TIC80_VERSION = 1.1.2837
TIC80_SOURCE = 	archive/refs/tags/v1.1.2837.tar.gz
TIC80_SITE = https://github.com/nesbox/TIC-80
TIC80_LICENSE = MIT
TIC80_DEPENDENCIES = libpipewire-0.3-dev libwayland-dev libsdl2-dev ruby-dev libcurl4-openssl-dev libglvnd-dev libglu1-mesa-dev freeglut3-dev

TIC80_CONF_OPTS = -DBUILD_SDLGPU=On
TIC80_CONF_OPTS += -DBUILD_WITH_ALL=On
TIC80_CONF_OPTS += -DBUILD_STATIC=On

$(eval $(cmake-package))
