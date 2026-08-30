#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
################################################################################
#
# linuxloader
#
################################################################################

LINUXLOADER_VERSION = v3.0.10
LINUXLOADER_SITE = $(call github,lindbergh-loader,linuxloader,$(LINUXLOADER_VERSION))
LINUXLOADER_LICENSE = CC-BY-SA-4.0
LINUXLOADER_LICENSE_FILES = LICENSE.md
LINUXLOADER_EMULATOR_INFO = linuxloader.emulator.yml

ifeq ($(BR2_x86_64),y)
LINUXLOADER_DEPENDENCIES = wine-x86 dmidecode ossp

# On x86_64, Batocera runs linuxloader via wine/multilib
define LINUXLOADER_CONFIGURE_CMDS
	:
endef
define LINUXLOADER_BUILD_CMDS
	:
endef
define LINUXLOADER_INSTALL_TARGET_CMDS
	:
endef
endif

ifeq ($(BR2_i386),y)
LINUXLOADER_DEPENDENCIES += alsa-lib alsa-plugins alsa-utils faudio libfreeglut
LINUXLOADER_DEPENDENCIES += libglu pcsc-lite libbsd libglew sdl3 sdl3_image sdl3_ttf
LINUXLOADER_DEPENDENCIES += ncurses openal pipewire udev vulkan-loader zlib expat
LINUXLOADER_DEPENDENCIES += xlib_libX11 xlib_libXcursor xlib_libXrandr xlib_libXext 
LINUXLOADER_DEPENDENCIES += xlib_libXi xlib_libXmu xlib_libXScrnSaver

define LINUXLOADER_FIX_CMAKELISTS
	# Allow dynamic linking of FAudio instead of forcing static
	$(SED) 's/-Wl,-Bstatic -lFAudio -Wl,-Bdynamic/-lFAudio/g' $(@D)/CMakeLists.txt
	# Prevent fopen / fopen64 duplicate symbol collision in filesystemShared.c
	$(SED) 's/-D_GNU_SOURCE/-D_GNU_SOURCE -U_FILE_OFFSET_BITS -D_FILE_OFFSET_BITS=32/g' $(@D)/CMakeLists.txt
endef
LINUXLOADER_POST_PATCH_HOOKS += LINUXLOADER_FIX_CMAKELISTS

define LINUXLOADER_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/linuxloader/extralibs

    # Main binaries & libraries built by CMake
    cp -fv $(LINUXLOADER_BUILDDIR)/linuxloader $(TARGET_DIR)/usr/bin/linuxloader/
    cp -fv $(LINUXLOADER_BUILDDIR)/linuxloader.so $(TARGET_DIR)/usr/bin/linuxloader/
    cp -fav $(LINUXLOADER_BUILDDIR)/lib*.so* $(TARGET_DIR)/usr/bin/linuxloader/extralibs/

    # Extract and copy repo bundled libraries
    if [ -f $(@D)/libs/linux_x86/Cg-3.1.zip ]; then \
        unzip -o $(@D)/libs/linux_x86/Cg-3.1.zip -d $(TARGET_DIR)/usr/bin/linuxloader/extralibs/; \
    fi
    cp -fv $(@D)/libs/linux_x86/libCg.so $(TARGET_DIR)/usr/bin/linuxloader/extralibs/libCg2.so
    cp -fv $(@D)/libs/linux_x86/libopenal.so.0 $(TARGET_DIR)/usr/bin/linuxloader/extralibs/
    cp -fv $(@D)/libs/linux_x86/libcrypto.so.0.9.7 $(TARGET_DIR)/usr/bin/linuxloader/extralibs/
    cp -fv $(@D)/libs/linux_x86/libssl.so.0.9.7 $(TARGET_DIR)/usr/bin/linuxloader/extralibs/

    # Critical NVIDIA / Posix symlinks
    ln -sf libposixtime.so $(TARGET_DIR)/usr/bin/linuxloader/extralibs/libposixtime.so.1
    ln -sf libposixtime.so $(TARGET_DIR)/usr/bin/linuxloader/extralibs/libposixtime.so.2.4
    ln -sf libkswapapi.so $(TARGET_DIR)/usr/bin/linuxloader/extralibs/libGLcore.so.1
    ln -sf libkswapapi.so $(TARGET_DIR)/usr/bin/linuxloader/extralibs/libnvidia-tls.so.1

    # Batocera package overrides / configs
    cp -fv $(LINUXLOADER_PKGDIR)/*.ini $(TARGET_DIR)/usr/bin/linuxloader/
    cp -fav $(LINUXLOADER_PKGDIR)/lib*.so* $(TARGET_DIR)/usr/bin/linuxloader/extralibs/
endef
endif

define LINUXLOADER_CROSSHAIRS
    mkdir -p $(TARGET_DIR)/usr/bin/linuxloader/crosshairs
    cp -fav $(LINUXLOADER_PKGDIR)/crosshairs/* $(TARGET_DIR)/usr/bin/linuxloader/crosshairs/
endef

LINUXLOADER_POST_INSTALL_TARGET_HOOKS += LINUXLOADER_CROSSHAIRS

$(eval $(cmake-package))
$(eval $(emulator-info-package))
