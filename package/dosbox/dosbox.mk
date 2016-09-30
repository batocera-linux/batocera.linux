################################################################################
#
# DosBox
#
################################################################################

DOSBOX_VERSION_TAG = 0.74
DOSBOX_VERSION = r3989
DOSBOX_SITE =  svn://svn.code.sf.net/p/dosbox/code-0/dosbox/trunk 
DOSBOX_SITE_METHOD = svn
DOSBOX_LICENSE = GPL2
DOSBOX_LICENSE_FILES = COPYING
DOSBOX_DEPENDENCIES = sdl2 zlib libpng libogg libvorbis sdl_sound

DOSBOX_LDFLAGS = -L$(STAGING_DIR)/usr/lib
DOSBOX_CFLAGS = -I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/SDL2 -I$(STAGING_DIR)/usr/include/SDL

define DOSBOX_CONFIGURE_CMDS
        (cd $(@D); ./autogen.sh; \
        $(TARGET_CONFIGURE_ARGS) \
                $(TARGET_CONFIGURE_OPTS) \
                CFLAGS="$(TARGET_CFLAGS) $(DOSBOX_CFLAGS)" \
                CXXFLAGS="$(TARGET_CXXFLAGS) $(DOSBOX_CFLAGS)" \
                CPPFLAGS="$(TARGET_CPPFLAGS) $(DOSBOX_CFLAGS)" \
                LDFLAGS="$(TARGET_LDFLAGS) $(DOSBOX_LDFLAGS)" \
                CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
		LIBS="-lvorbisfile -lvorbis -logg" \
                ./configure --host="$(GNU_TARGET_NAME)" \
                --enable-core-inline --prefix=/usr \
                --enable-dynrec --enable-unaligned_memory \
                --disable-opengl --with-sdl=sdl2 \
                --with-sdl-prefix="$(STAGING_DIR)/usr"; \
        )
endef

$(eval $(autotools-package))
