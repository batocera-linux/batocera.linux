################################################################################
#
# SFML library
#
################################################################################
# Version.: Release 2.5.1
SFML_VERSION = 2.5.1
SFML_SITE = $(call github,SFML,SFML,$(SFML_VERSION))
SFML_LICENSE = GPLv3
SFML_DEPENDENCIES = sdl2 gstreamer1 gst1-plugins-base

SFML_CONF_OPTS = -DSFML_OPENGL_ES=ON

define SFML_INSTALL_TARGET_CMDS
endef

$(eval $(cmake-package))
