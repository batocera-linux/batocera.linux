################################################################################
#
# RE3
#
################################################################################
# Version.: Commits on Jun 29, 2021
RE3_VERSION = 22e8e0eff8bc7444fc1d359048263cb715ca11e3
RE3_SITE = $(call github,GTAmodding,re3,$(RE3_VERSION))
RE3_LICENSE = Non-commercial
RE3_DEPENDENCIES = sdl2 sdl2_mixer freetype pcre jpeg libpng cairo ffmpeg libcurl

define RE3_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin

	cp -pr $(@D)/$(BR2_ARCH)/Release/bin/re3 $(TARGET_DIR)/usr/bin/re3
endef

$(eval $(cmake-package))
