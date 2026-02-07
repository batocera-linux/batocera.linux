################################################################################
#
# wlrctl
#
################################################################################

WLRCTL_VERSION = v0.2.2
WLRCTL_SITE = https://git.sr.ht/~brocellous/wlrctl/archive
WLRCTL_SOURCE = $(WLRCTL_VERSION).tar.gz
WLRCTL_LICENSE = MIT
WLRCTL_SITE_METHOD = wget

WLRCTL_DEPENDENCIES = wayland

WLRCTL_CONF_OPTS = --prefix=/usr -Dzsh-completions=false

$(eval $(meson-package))

