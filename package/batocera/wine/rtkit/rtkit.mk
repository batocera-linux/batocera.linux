################################################################################
#
# rtkit
#
################################################################################

RTKIT_VERSION = v0.14
RTKIT_SOURCE = rtkit-$(RTKIT_VERSION).tar.gz
RTKIT_SITE = https://gitlab.freedesktop.org/pipewire/rtkit/-/archive/$(RTKIT_VERSION)
# host-vim needed for xxd 
RTKIT_DEPENDENCIES = dbus host-vim libcap polkit

define RTKIT_USERS
	rtkit -1 rtkit -1 * - - - Realtime Policy and Watchdog Daemon
endef

$(eval $(meson-package))
