################################################################################
#
# supermodel
#
################################################################################
# Version: Commits on Oct 1, 2024
SUPERMODEL_VERSION = 161f1e39b43828fc81462d3903f5b233432515b3
SUPERMODEL_SITE = $(call github,trzy,Supermodel,$(SUPERMODEL_VERSION))
SUPERMODEL_DEPENDENCIES = sdl2 zlib libzip sdl2_net
SUPERMODEL_LICENSE = GPLv3

ifeq ($(BR2_PACKAGE_LIBGLEW),y)
SUPERMODEL_DEPENDENCIES += libglew
endif

define SUPERMODEL_BUILD_CMDS
	cp $(@D)/Makefiles/Makefile.UNIX $(@D)/Makefile
	$(SED) "s|CC = gcc|CC = $(TARGET_CC)|g" $(@D)/Makefile
	$(SED) "s|CXX = g++|CXX = $(TARGET_CXX)|g" $(@D)/Makefile
	$(SED) "s|LD = gcc|LD = $(TARGET_CC)|g" $(@D)/Makefile
	$(SED) "s|sdl2-config|$(STAGING_DIR)/usr/bin/sdl2-config|g" $(@D)/Makefile
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile NET_BOARD=1 \
	    VERBOSE=1 ARCH=$(BR2_TARGET_OPTIMIZATION)
endef

define SUPERMODEL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/supermodel
	$(INSTALL) -D -m 0755 $(@D)/bin/supermodel \
	    $(TARGET_DIR)/usr/bin/supermodel
	$(INSTALL) -D -m 0644 $(@D)/Config/Games.xml \
	    $(TARGET_DIR)/usr/share/supermodel/Games.xml
	$(INSTALL) -D -m 0644 $(@D)/Config/Supermodel.ini \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel.ini.template
	$(INSTALL) -D -m 0644 $(@D)/Config/Supermodel.ini \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputAccelerator = "KEY_UP,JOY1_UP"|InputAccelerator = "KEY_UP,JOY1_RZAXIS_POS"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputBrake = "KEY_DOWN,JOY1_DOWN"|InputBrake = "KEY_DOWN,JOY1_ZAXIS_POS"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputGearShift1 = "KEY_Q,JOY1_BUTTON5"|InputGearShift1 = "KEY_Q"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputGearShift2 = "KEY_W,JOY1_BUTTON6"|InputGearShift2 = "KEY_W"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputGearShift3 = "KEY_E,JOY1_BUTTON7"|InputGearShift3 = "KEY_E"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputGearShift4 = "KEY_R,JOY1_BUTTON8"|InputGearShift4 = "KEY_R"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputGearShiftUp = "KEY_Y"|InputGearShiftUp = "KEY_Y,JOY1_BUTTON6,JOY1_RYAXIS_NEG"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	$(SED) 's|InputGearShiftDown = "KEY_H"|InputGearShiftDown = "KEY_H,JOY1_BUTTON5,JOY1_RYAXIS_POS"|g' \
	    $(TARGET_DIR)/usr/share/supermodel/Supermodel-Driving.ini.template
	mkdir -p $(TARGET_DIR)/usr/share/supermodel/Assets
	$(INSTALL) -D -m 0644 $(@D)/Assets/* $(TARGET_DIR)/usr/share/supermodel/Assets/
endef

define SUPERMODEL_LINE_ENDINGS_FIXUP
	# DOS2UNIX Supermodel.ini and Main.cpp - patch system does not support different line endings
	sed -i -E -e "s|\r$$||g" $(@D)/Src/OSD/SDL/Main.cpp
	sed -i -E -e "s|\r$$||g" $(@D)/Src/Inputs/Inputs.cpp
	sed -i -E -e "s|\r$$||g" $(@D)/Src/Graphics/New3D/R3DShaderTriangles.h
	sed -i -E -e "s|\r$$||g" $(@D)/Src/OSD/Unix/FileSystemPath.cpp
endef

define SUPERMODEL_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy $(TARGET_DIR)/usr/share/supermodel
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/supermodel/model3.supermodel.keys \
	    $(TARGET_DIR)/usr/share/evmapy
    cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/supermodel/NVRAM \
	    $(TARGET_DIR)/usr/share/supermodel
endef

SUPERMODEL_PRE_PATCH_HOOKS += SUPERMODEL_LINE_ENDINGS_FIXUP

SUPERMODEL_POST_INSTALL_TARGET_HOOKS += SUPERMODEL_POST_PROCESS

$(eval $(generic-package))
