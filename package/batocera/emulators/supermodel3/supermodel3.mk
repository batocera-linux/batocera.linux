################################################################################
#
# SUPERMODEL3
#
################################################################################

SUPERMODEL3_VERSION = r845
SUPERMODEL3_SITE = https://svn.code.sf.net/p/model3emu/code/trunk
SUPERMODEL3_SITE_METHOD=svn
SUPERMODEL3_DEPENDENCIES = sdl2 zlib libglew libzip sdl2_net
SUPERMODEL3_LICENSE = GPLv3

define SUPERMODEL3_BUILD_CMDS
	$(SED) "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+CC =+CC ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+CXX =+CXX ?=+g" $(@D)/Makefiles/Makefile.UNIX
	$(SED) "s+LD =+LD ?=+g" $(@D)/Makefiles/Makefile.UNIX
	#$(SED) "s+-march=native+-msse+g" $(@D)/Makefiles/Makefile.inc
	CXX="$(TARGET_CXX)" \
	CC="$(TARGET_CC)" \
	LD="$(TARGET_CC)" \
	$(MAKE) -C $(@D)/ -f Makefiles/Makefile.UNIX
endef

define SUPERMODEL3_INSTALL_TARGET_CMDS
	# Ensure Supermodel is in it's own directory with specific subdirectories
	mkdir -p $(TARGET_DIR)/usr/bin/supermodel/
	mkdir -p $(TARGET_DIR)/usr/bin/supermodel/Config/
	mkdir -p $(TARGET_DIR)/usr/bin/supermodel/NVRAM/
	mkdir -p $(TARGET_DIR)/usr/bin/supermodel/Saves/
	# Add directory for EmulationStation
	mkdir -p  $(TARGET_DIR)/userdata/roms/model3/
	$(INSTALL) -D $(@D)/bin/supermodel $(TARGET_DIR)/usr/bin/supermodel/
	cp -R $(@D)/Config/* $(TARGET_DIR)/usr/bin/supermodel/Config/
endef

$(eval $(generic-package))
