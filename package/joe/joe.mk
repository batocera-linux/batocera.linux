################################################################################
#
# joe
#
################################################################################

JOE_VERSION = 4.6
JOE_SITE = http://downloads.sourceforge.net/project/joe-editor/JOE%20sources/joe-$(JOE_VERSION)
JOE_LICENSE = GPL-2.0+
JOE_LICENSE_FILES = COPYING

ifeq ($(BR2_PACKAGE_NCURSES),y)
JOE_DEPENDENCIES += ncurses
JOE_CONF_OPTS += --enable-curses
else
JOE_CONF_OPTS += --disable-curses
endif

ifneq ($(BR2_PACKAGE_JOE_FULL),y)
define JOE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/joe/joe $(TARGET_DIR)/usr/bin/joe
endef
endif

$(eval $(autotools-package))
