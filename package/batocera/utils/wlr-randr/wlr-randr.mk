################################################################################
#
# WLR-RANDR
#
################################################################################

WLR_RANDR_VERSION = 0.3.0
WLR_RANDR_SOURCE = wlr-randr-$(WLR_RANDR_VERSION).tar.gz
WLR_RANDR_SITE = https://git.sr.ht/~emersion/wlr-randr/refs/download/v$(WLR_RANDR_VERSION)
WLR_RANDR_LICENSE = MIT
WLR_RANDR_LICENSE_FILES = LICENSE

$(eval $(meson-package))
