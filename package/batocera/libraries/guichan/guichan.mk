################################################################################
#
# guichan
#
################################################################################

GUICHAN_VERSION = 0.8.1
GUICHAN_SOURCE = guichan-$(GUICHAN_VERSION).tar.gz
GUICHAN_SITE = http://pkgs.fedoraproject.org/repo/pkgs/guichan/guichan-$(GUICHAN_VERSION).tar.gz/f9ace11cc70d3ba60b62347172334a5f

# broken urls
#http://guichan.googlecode.com/files/guichan-0.8.1.tar.gz
#http://guichan.sourceforge.net/wiki/

GUICHAN_LICENSE = BSD
GUICHAN_DEPENDENCIES = sdl sdl_image

GUICHAN_INSTALL_STAGING = YES

GUICHAN_CONF_OPTS += HAVE_SDL=yes
GUICHAN_CPPFLAGS += -I$(STAGING_DIR)/usr/include/SDL
GUICHAN_CFLAGS += -I$(STAGING_DIR)/usr/include/SDL

define GUICHAN_CONFIGURE_CMDS
        (cd $(@D); \
        $(TARGET_CONFIGURE_ARGS) \
                $(TARGET_CONFIGURE_OPTS) \
                CFLAGS="$(TARGET_CFLAGS) $(GUICHAN_CFLAGS)" \
                CXXFLAGS="$(TARGET_CXXFLAGS) $(GUICHAN_CFLAGS)" \
                CPPFLAGS="$(TARGET_CPPFLAGS) $(GUICHAN_CFLAGS)" \
                LDFLAGS="$(TARGET_LDFLAGS) $(GUICHAN_LDFLAGS)" \
                CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
                ./configure --host="$(GNU_TARGET_NAME)" \
	        --prefix=/usr $(GUICHAN_CONF_OPTS) \
        )
endef

$(eval $(autotools-package))
