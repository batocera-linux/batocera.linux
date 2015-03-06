################################################################################
#
# Scummvm
#
################################################################################

SCUMMVM_VERSION = 763a962e1456fd8402be4992ab9069e9e507ebc8
SCUMMVM_REPO = scummvm

SCUMMVM_SITE = $(call github,$(SCUMMVM_REPO),scummvm,$(SCUMMVM_VERSION))

SCUMMVM_LICENSE = GPL2
SCUMMVM_DEPENDENCIES = sdl zlib jpeg-turbo libmpeg2 libogg libvorbis flac libmad libpng libtheora \
	faad2 fluidsynth freetype 

SCUMMVM_ADDITIONAL_FLAGS= -I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux -lpthread -lm -L$(STAGING_DIR)/usr/lib -lbcm_host -lGLESv2 -lEGL -lvchostif 

SCUMMVM_CONF_ENV += RANLIB="$(TARGET_RANLIB)" STRIP="$(TARGET_STRIP)" AR="$(TARGET_AR) cru" AS="$(TARGET_AS)"
SCUMMVM_CONF_OPTS += --with-sdl-prefix="$(STAGING_DIR)/usr/bin"

SCUMMVM_MAKE_OPTS += RANLIB="$(TARGET_RANLIB)" STRIP="$(TARGET_STRIP)" AR="$(TARGET_AR) cru" AS="$(TARGET_AS)" LD="$(TARGET_CXX)" 
#define SCUMMVM_ADD_EXECUTABLE
#	$(SED) "s|RANLIB := ranlib|RANLIB 
#STRIP := strip
#AR := ar cru
#AS := as

#SCUMMVM_POST_CONFIGURE_HOOKS += SCUMMVM_ADD_EXECUTABLES
$(eval $(autotools-package))
