################################################################################
#
# GRIM
#
################################################################################

GRIM_VERSION = 1.4.0
GRIM_SOURCE = grim-$(GRIM_VERSION).tar.gz
GRIM_SITE = https://git.sr.ht/~emersion/grim/refs/download/v$(GRIM_VERSION)
GRIM_LICENSE = MIT
GRIM_LICENSE_FILES = LICENSE

GRIM_CONF_OPTS = -Dman-pages=disabled -Dwerror=false

$(eval $(meson-package))
