################################################################################
#
# sdl2-touch-test
#
################################################################################

SDL2_TOUCH_TEST_VERSION = 1.0
SDL2_TOUCH_TEST_SOURCE =

define SDL2_TOUCH_TEST_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) \
		-o $(@D)/sdl_test $(SDL2_TOUCH_TEST_PKGDIR)/sdl_test.c -lSDL2
endef

define SDL2_TOUCH_TEST_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/sdl_test $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
