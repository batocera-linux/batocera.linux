################################################################################
#
# wtype
#
################################################################################

WTYPE_VERSION = v0.4
WTYPE_SITE = $(call github,atx,wtype,$(WTYPE_VERSION))
WTYPE_LICENSE = MIT License
WTYPE_LICENSE_FILES = LICENSE
WTYPE_DEPENDENCIES = libxkbcommon wayland

$(eval $(meson-package))
