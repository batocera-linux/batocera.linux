################################################################################
#
# SugarBoxV2
#
################################################################################
# Version: Commits on Nov 29, 2023
SUGARBOX_VERSION = d7d1d39111efb9c44fc956beea076ee243774dc1
SUGARBOX_SITE = https://github.com/Tom1975/SugarboxV2.git
SUGARBOX_SITE_METHOD=git
SUGARBOX_GIT_SUBMODULES=YES
SUGARBOX_LICENSE = MIT
SUGARBOX_DEPENDENCIES = qt6base qt6tools qt6websockets

ifeq ($(BR2_PACKAGE_SWAY),y)
SUGARBOX_DEPENDENCIES += qt6wayland
endif

SUGARBOX_SUPPORTS_IN_SOURCE_BUILD = NO

SUGARBOX_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
SUGARBOX_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
SUGARBOX_CONF_OPTS += -DALSOFT_UPDATE_BUILD_VERSION=OFF
SUGARBOX_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/sugarbox/"

SUGARBOX_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
  SUGARBOX_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lmali_hook -Wl,--whole-archive -lmali_hook_injector -Wl,--no-whole-archive -lmali"
endif

define SUGARBOX_QT6_FIX_CMAKE
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/sugarbox/CMakeLists.txt $(@D)/Sugarbox/CMakeLists.txt
endef

SUGARBOX_PRE_CONFIGURE_HOOKS += SUGARBOX_QT6_FIX_CMAKE

$(eval $(cmake-package))
