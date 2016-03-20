################################################################################
#
# omxplayer
#
################################################################################

# omxplayer based on fmpeg 2.8.1
OMXPLAYER_VERSION = 1cd53be67b6be027cb1c70d20582b851d18223a9
OMXPLAYER_SITE = $(call github,popcornmix,omxplayer,$(OMXPLAYER_VERSION))
OMXPLAYER_DEPENDENCIES = rpi-userland boost pcre freetype ffmpeg

OMXPLAYER_CONFIG_OPT = \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	CXXCP="$(CXX) -E" \
	AR="$(TARGET_CROSS)ar" \
	LD="$(TARGET_LD)" \
	OBJDUMP="$(TARGET_CROSS)objdump" \
	RANLIB="$(TARGET_CROSS)ranlib" \
	STRIP="$(TARGET_CROSS)strip" \
	PATH=$(HOST_DIR)/usr/bin:$(PATH) \
	LDFLAGS="$(TARGET_LDFLAGS) -L$(STAGING_DIR)/lib -L$(STAGING_DIR)/usr/lib -Lpcre/build -lvchostif -lc -lWFC -lGLESv2 -lEGL -lbcm_host -lopenmaxil -lfreetype -lz"\
	INCLUDES="-isystem./ -isystem./linux \
		-isystem$(STAGING_DIR)/usr/include \
		-isystem$(STAGING_DIR)/usr/include/interface/vcos/pthreads \
		-isystem$(STAGING_DIR)/usr/include/interface/vmcs_host/linux \
		-isystem$(STAGING_DIR)/usr/include/freetype2 \
		-isystem$(STAGING_DIR)/usr/include/dbus-1.0 \
		-isystem$(STAGING_DIR)/usr/lib/dbus-1.0/include"

define OMXPLAYER_BUILD_CMDS
	$(MAKE) -C $(@D) $(OMXPLAYER_CONFIG_OPT) omxplayer.bin
endef

define OMXPLAYER_INSTALL_TARGET_CMDS
	$(INSTALL) -m 755 $(@D)/omxplayer.bin $(TARGET_DIR)/usr/bin/omxplayer.bin
	$(INSTALL) -m 755 $(@D)/omxplayer $(TARGET_DIR)/usr/bin/omxplayer
	mkdir -p $(TARGET_DIR)/usr/share/fonts/truetype/freefont/
	$(INSTALL) -m 644 $(@D)/fonts/FreeSans.ttf $(TARGET_DIR)/usr/share/fonts/truetype/freefont/
endef

define OMXPLAYER_UNINSTALL_TARGET_CMDS
	-rm $(TARGET_DIR)/usr/bin/omxplayer.bin
	-rm $(TARGET_DIR)/usr/bin/omxplayer
	-rm $(TARGET_DIR)/usr/share/fonts/FreeSans.ttf
endef

$(eval $(generic-package))
