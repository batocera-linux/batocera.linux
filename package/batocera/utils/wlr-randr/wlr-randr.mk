################################################################################
#
# wlr-randr
#
################################################################################

WLR_RANDR_VERSION = 0.5.0
WLR_RANDR_SITE = https://gitlab.freedesktop.org/emersion/wlr-randr/-/archive/$(WLR_RANDR_VERSION)
WLR_RANDR_LICENSE = MIT
WLR_RANDR_LICENSE_FILES = LICENSE

WLR_RANDR_DEPENDENCIES = wayland

$(eval $(meson-package))
