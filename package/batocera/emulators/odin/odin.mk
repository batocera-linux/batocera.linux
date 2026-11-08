################################################################################
#
# odin
#
################################################################################

# Version: Commits on Nov 8, 2026
ODIN_VERSION = 6ebf2b40ccbca9534d1a0e58b7602db11e4485d9
ODIN_SITE = $(call github,Tovarichtch,Odin,$(ODIN_VERSION))
ODIN_LICENSE = GPL-3.0+
ODIN_LICENSE_FILES = LICENSE
ODIN_EMULATOR_INFO = odin.emulator.yml

ODIN_DEPENDENCIES = host-glslang host-pkgconf jansson sdl3 vulkan-headers xlib_libX11

ODIN_CONF_OPTS = \
    -DCMAKE_BUILD_TYPE= \
    -DODIN_NATIVE=OFF \
    -DODIN_BUNDLED_LIBS=OFF \
    -DGLSLANG=$(HOST_DIR)/bin/glslangValidator \
    -DODIN_VERSION=$(shell echo $(ODIN_VERSION) | cut -c1-7)

ifeq ($(BR2_x86_64),y)
ODIN_DEPENDENCIES += libglew
else
ODIN_DEPENDENCIES += libgles
ODIN_CONF_OPTS += -DODIN_GLES=ON
endif

define ODIN_INSTALL_NVRAM
	mkdir -p $(TARGET_DIR)/usr/share/odin/nvram
	$(TAR) -xJf $(ODIN_PKGDIR)/nvram.tar.xz -C $(TARGET_DIR)/usr/share/odin/nvram
endef

ODIN_POST_INSTALL_TARGET_HOOKS += ODIN_INSTALL_NVRAM

$(eval $(cmake-package))
$(eval $(emulator-info-package))
