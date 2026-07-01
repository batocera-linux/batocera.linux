################################################################################
#
# drastic
#
################################################################################

DRASTIC_VERSION = r2.5.2.2
DRASTIC_SOURCE = drastic.tar.gz
DRASTIC_SITE = https://github.com/dmanlfc/drastic/raw/refs/heads/main
DRASTIC_EMULATOR_INFO = drastic.emulator.yml

define DRASTIC_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) -shared -fPIC \
		-o $(@D)/libdrastouch.so $(DRASTIC_PKGDIR)/libdrastouch.c -ldl
endef

define DRASTIC_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/share/drastic
	cp -pr $(@D)/drastic_aarch64/* $(TARGET_DIR)/usr/share/drastic
	cp -f $(@D)/libdrastouch.so  $(TARGET_DIR)/usr/lib/
	chmod +x $(TARGET_DIR)/usr/share/drastic/drastic
	mkdir -p $(TARGET_DIR)/usr/share/drastic/microphone
	cp -f $(DRASTIC_PKGDIR)/microphone.wav $(TARGET_DIR)/usr/share/drastic/microphone/
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
