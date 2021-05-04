################################################################################
#
# rtkit
#
################################################################################

RTKIT_VERSION = v0.13
RTKIT_SITE = $(call github,heftig,RTKIT,$(RTKIT_VERSION))
# host-vim needed for xxd 
RTKIT_DEPENDENCIES = dbus host-vim libcap polkit

define RTKIT_USERS
	rtkit -1 rtkit -1 * - - - Realtime Policy and Watchdog Daemon
endef

$(eval $(meson-package))
