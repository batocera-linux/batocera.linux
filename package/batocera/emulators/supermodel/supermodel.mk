################################################################################
#
# SUPERMODEL
#
################################################################################

SUPERMODEL_VERSION = r845
SUPERMODEL_SITE = https://svn.code.sf.net/p/model3emu/code/trunk
SUPERMODEL_SITE_METHOD=svn
SUPERMODEL_DEPENDENCIES = sdl2 zlib libglew libzip sdl2_net
SUPERMODEL_LICENSE = GPLv3

define SUPERMODEL_BUILD_CMDS
	cp $(@D)/Makefiles/Makefile.UNIX $(@D)/Makefile
	$(SED) "s|CC = gcc|CC = $(TARGET_CC)|g" $(@D)/Makefile
	$(SED) "s|CXX = g++|CXX = $(TARGET_CXX)|g" $(@D)/Makefile
	$(SED) "s|LD = gcc|LD = $(TARGET_CC)|g" $(@D)/Makefile
	$(SED) "s|sdl2-config|$(STAGING_DIR)/usr/bin/sdl2-config|g" $(@D)/Makefile
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile VERBOSE=1
endef

define SUPERMODEL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/supermodel $(TARGET_DIR)/usr/bin/supermodel
	$(INSTALL) -D -m 0644 $(@D)/Config/Games.xml $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/supermodel/Games.xml
	$(INSTALL) -D -m 0644 $(@D)/Config/Supermodel.ini $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/supermodel/Supermodel.ini.orig
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/supermodel/NVRAM/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/saves/supermodel/
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/screenshots/supermodel/
endef

define SUPERMODEL_LINE_ENDINGS_FIXUP
	# DOS2UNIX Supermodel.ini and Main.cpp - patch system does not support different line endings
	sed -i -E -e "s|\r$$||g" $(@D)/Src/OSD/SDL/Main.cpp
	sed -i -E -e "s|\r$$||g" $(@D)/Src/Inputs/Inputs.cpp
endef

define SUPERMODEL_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/supermodel/supermodel.keys $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/supermodel/Supermodel.ini $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/supermodel/Supermodel.ini
endef

SUPERMODEL_PRE_PATCH_HOOKS += SUPERMODEL_LINE_ENDINGS_FIXUP

SUPERMODEL_POST_INSTALL_TARGET_HOOKS += SUPERMODEL_POST_PROCESS

$(eval $(generic-package))
