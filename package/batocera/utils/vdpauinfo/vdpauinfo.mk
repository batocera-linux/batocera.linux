################################################################################
#
# vdpauinfo
#
################################################################################

VDPAUINFO_VERSION = 1.5
VDPAUINFO_SOURCE = vdpauinfo-$(VDPAUINFO_VERSION).tar.gz
VDPAUINFO_SITE = https://gitlab.freedesktop.org/vdpau/vdpauinfo/-/archive/$(VDPAUINFO_VERSION)
VDPAUINFO_LICENSE = MIT
VDPAUINFO_LICENSE_FILES = COPYING

VDPAUINFO_DEPENDENCIES = libvdpau xlib_libX11

define VDPAUINFO_RUN_AUTOGEN
	cd $(@D) && PATH=$(BR_PATH) ./autogen.sh
endef

VDPAUINFO_PRE_CONFIGURE_HOOKS += VDPAUINFO_RUN_AUTOGEN

$(eval $(autotools-package))
