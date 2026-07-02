################################################################################
#
# sdl2-touch-test
#
################################################################################

SDL2_TOUCH_TEST_VERSION = 1.1
SDL2_TOUCH_TEST_SOURCE =
SDL2_TOUCH_TEST_DEPENDENCIES = sdl2 sdl2_ttf udev

define SDL2_TOUCH_TEST_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) \
		-o $(@D)/sdl2-touch-test $(SDL2_TOUCH_TEST_PKGDIR)/sdl2-touch-test.c \
		-lSDL2 -lSDL2_ttf -ludev -lm
endef

define SDL2_TOUCH_TEST_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/sdl2-touch-test $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
