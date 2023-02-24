################################################################################
#
# swaybg
#
################################################################################

SWAYBG_VERSION = v1.2.0
SWAYBG_SITE = $(call github,swaywm,swaybg,$(SWAYBG_VERSION))
SWAYBG_LICENSE = MIT
SWAYBG_LICENSE_FILES = LICENSE
SWAYBG_DEPENDENCIES = wayland wayland-protocols cairo

SWAYBG_CONF_OPTS = -Dman-pages=disabled

$(eval $(meson-package))
