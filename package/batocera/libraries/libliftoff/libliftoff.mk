################################################################################
#
# LIBLIFTOFF
#
################################################################################

LIBLIFTOFF_VERSION = 0.4.0
LIBLIFTOFF_SITE = https://gitlab.freedesktop.org/emersion/libliftoff/-/releases/v$(LIBLIFTOFF_VERSION)/downloads
LIBLIFTOFF_LICENSE = MIT
LIBLIFTOFF_LICENSE_FILES = LICENSE

$(eval $(meson-package))
