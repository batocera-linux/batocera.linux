################################################################################
#
# piFBA
#
################################################################################

PIFBA_VERSION = master
PIFBA_SITE = $(call github,digitallumberjack,pifba,master)

PIFBA_LICENSE = MIT
PIFBA_DEPENDENCIES = sdl2 alsa-lib rpi-userland

SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl2-config
SDL_FLAGS=`$(SDL_CONFIG) --cflags`
SDL_LIBS=`$(SDL_CONFIG) --libs`

PIFBA_CFLAGS=$(TARGET_CFLAGS) -Wall -W -Wno-write-strings -O3 -DOOPSWARE_FIX -D_T="" -DNEOGEO_HACKS -D__cdecl="" \
	-D__fastcall="" -DUSE_SPEEDHACKS -DNEO_DISPLAY_OVERSCAN -falign-functions=32 -falign-loops -falign-labels -falign-jumps -fomit-frame-pointer -ffast-math \
	-fexpensive-optimizations -finline -finline-functions -mstructure-size-boundary=32 -frename-registers 

PIFBA_CXXFLAGS=$(TARGET_CXXFLAGS) -DQWS -fno-exceptions -fno-rtti -Wall -W -Wno-write-strings -O3 -DOOPSWARE_FIX -D_T="" -DNEOGEO_HACKS \
	-D__cdecl="" -D__fastcall="" -DUSE_SPEEDHACKS -DNEO_DISPLAY_OVERSCAN -falign-functions=32 -falign-loops -falign-labels -falign-jumps -fomit-frame-pointer -ffast-math \
	-fexpensive-optimizations -finline -finline-functions -mstructure-size-boundary=32 -frename-registers


PIFBA_LIBS=-lz -lpthread -lm -lpthread -lSDL2 -L$(STAGING_DIR)/usr/lib -lbcm_host -lGLESv2 -lEGL -lglib-2.0 -lasound -lrt -lvchostif

PIFBA_INCLUDES=-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads \
		-I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux $(SDL_FLAGS) \
		-I$(STAGING_DIR)/usr/include/glib-2.0 -I$(STAGING_DIR)/usr/lib/glib-2.0/include \
		-I$(@D)/rpi -I$(@D)/burn -I$(@D)/burn/neogeo -I$(@D)/burn/capcom -I$(@D)/burn/cave -I$(@D)/burn/toaplan -I$(@D)/cpu/cyclone \
		-I$(@D)/cpu/z80 -I$(@D)/cpu/cz80 -I$(@D)/cpu/nec -I$(@D)/cpu/sh2 -I$(@D)/burn/misc 

define PIFBA_BUILD_CMDS
        $(MAKE) CFLAGS="$(PIFBA_CFLAGS)" CXXFLAGS="$(PIFBA_CXXFLAGS)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	INCPATH="$(PIFBA_INCLUDES)" LINK="$(TARGET_CXX)" LIBS="$(PIFBA_LIBS)" \
	-C $(@D)
endef
#define PIFBA_BUILD_CMDS
#	$(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
		CFLAGS="$(PIFBA_CFLAGS)" \
		CXXFLAGS="$(PIFBA_CXXFLAGS)" \
		LIBS="$(PIFBA_LIBS)" \
		INCPATH="$(PIFBA_INCLUDES)" \
		LINK="$(TARGET_CXX)" \
		-C $(@D)
#endef

define PIFBA_INSTALL_STAGING_CMDS
	$(INSTALL) -D -m 0755 $(@D)/fba2x $(STAGING_DIR)/usr/bin/fba2x
endef

define PIFBA_INSTALL_TARGET_CMDS
    	$(INSTALL) -D -m 0755 $(@D)/fba2x $(TARGET_DIR)/usr/bin/fba2x
endef

define PIFBA_RPI_FIXUP
	mkdir $(@D)/.obj
	$(SED) "s|strip|$(STAGING_DIR)/../bin/strip|g"  $(@D)/Makefile
endef

PIFBA_PRE_CONFIGURE_HOOKS += PIFBA_RPI_FIXUP

$(eval $(generic-package))
