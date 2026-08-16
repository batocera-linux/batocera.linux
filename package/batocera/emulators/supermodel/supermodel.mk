################################################################################
#
# supermodel
#
################################################################################
# Version: based on v0.3a-20260726 (Commits on Aug 17, 2026)
SUPERMODEL_VERSION = 6db4c4fba968c0da3d7785152fe89d100962684b
SUPERMODEL_SITE = $(call github,dmanlfc,Supermodel,$(SUPERMODEL_VERSION))
SUPERMODEL_DEPENDENCIES = sdl2 zlib libzip sdl2_net
SUPERMODEL_LICENSE = GPLv3
SUPERMODEL_EMULATOR_INFO = supermodel.emulator.yml

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
ifeq ($(BR2_PACKAGE_LIBGLEW),y)
SUPERMODEL_DEPENDENCIES += libglew
endif
ifeq ($(BR2_PACKAGE_LIBGLU),y)
SUPERMODEL_DEPENDENCIES += libglu
endif
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
SUPERMODEL_DEPENDENCIES += libgles
SUPERMODEL_CONF_OPTS += GLES=1
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
SUPERMODEL_DEPENDENCIES += wayland
SUPERMODEL_CONF_OPTS += WAYLAND=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
SUPERMODEL_DEPENDENCIES += vulkan-headers vulkan-loader
SUPERMODEL_CONF_OPTS += VULKAN=1
endif

define SUPERMODEL_BUILD_CMDS
	cp $(@D)/Makefiles/Makefile.UNIX $(@D)/Makefile
	$(SED) "s|CC = gcc|CC = $(TARGET_CC)|g" $(@D)/Makefile
	$(SED) "s|CXX = g++|CXX = $(TARGET_CXX)|g" $(@D)/Makefile
	$(SED) "s|LD = gcc|LD = $(TARGET_CC)|g" $(@D)/Makefile
	$(SED) "s|sdl2-config|$(STAGING_DIR)/usr/bin/sdl2-config|g" $(@D)/Makefile
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile \
	    ARCH=$(BR2_TARGET_OPTIMIZATION) $(SUPERMODEL_CONF_OPTS)
endef

define SUPERMODEL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/supermodel
	$(INSTALL) -D -m 0755 $(@D)/bin/supermodel \
	    $(TARGET_DIR)/usr/bin/supermodel
	$(INSTALL) -D -m 0644 $(@D)/Config/Games.xml \
	    $(TARGET_DIR)/usr/share/supermodel/Games.xml
	mkdir -p $(TARGET_DIR)/usr/share/supermodel/Assets
	$(INSTALL) -D -m 0644 $(@D)/Assets/* $(TARGET_DIR)/usr/share/supermodel/Assets/
endef

define SUPERMODEL_LINE_ENDINGS_FIXUP
	# DOS2UNIX Supermodel.ini and Main.cpp - patch system does not support different line endings
	sed -i -E -e "s|\r$$||g" $(@D)/Src/OSD/SDL/Main.cpp
	sed -i -E -e "s|\r$$||g" $(@D)/Src/Model3/Model3.cpp
	sed -i -E -e "s|\r$$||g" $(@D)/Src/Inputs/Inputs.cpp
	sed -i -E -e "s|\r$$||g" $(@D)/Src/Graphics/New3D/R3DShaderTriangles.h
	sed -i -E -e "s|\r$$||g" $(@D)/Src/OSD/Unix/FileSystemPath.cpp
endef

define SUPERMODEL_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy $(TARGET_DIR)/usr/share/supermodel
	cp -pr $(SUPERMODEL_PKGDIR)/NVRAM $(TARGET_DIR)/usr/share/supermodel
	cp -p $(SUPERMODEL_PKGDIR)/Supermodel.ini.template \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel.ini.template
endef

SUPERMODEL_PRE_PATCH_HOOKS += SUPERMODEL_LINE_ENDINGS_FIXUP

SUPERMODEL_POST_INSTALL_TARGET_HOOKS += SUPERMODEL_POST_PROCESS

$(eval $(generic-package))
$(eval $(emulator-info-package))
