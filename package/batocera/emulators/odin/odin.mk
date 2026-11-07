################################################################################
#
# odin
#
################################################################################
# Version: Commits on Nov 06, 2026
ODIN_VERSION = b9b47e466f82864b90b0b3c81e6364a7f4c0530a
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

$(eval $(cmake-package))
$(eval $(emulator-info-package))
