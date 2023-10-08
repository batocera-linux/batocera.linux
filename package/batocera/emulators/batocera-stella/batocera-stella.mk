################################################################################
#
# stella
#
################################################################################

BATOCERA_STELLA_VERSION = 6.7
BATOCERA_STELLA_SOURCE = stella-$(BATOCERA_STELLA_VERSION)-src.tar.xz
BATOCERA_STELLA_SITE = https://github.com/stella-emu/stella/releases/download/$(BATOCERA_STELLA_VERSION)
BATOCERA_STELLA_LICENSE = GPL-2.0+
BATOCERA_STELLA_LICENSE_FILES = Copyright.txt License.txt

BATOCERA_STELLA_DEPENDENCIES = sdl2

BATOCERA_STELLA_CONF_OPTS = \
	--host=$(GNU_TARGET_NAME) \
	--prefix=/usr \
	--with-sdl-prefix=$(STAGING_DIR)/usr \
	--enable-release

ifeq ($(BR2_PACKAGE_LIBPNG),y)
BATOCERA_STELLA_CONF_OPTS += --enable-png
BATOCERA_STELLA_DEPENDENCIES += libpng
else
BATOCERA_STELLA_CONF_OPTS += --disable-png
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
BATOCERA_STELLA_CONF_OPTS += --enable-zip
BATOCERA_STELLA_DEPENDENCIES += zlib
else
BATOCERA_STELLA_CONF_OPTS += --disable-zip
endif

# The configure script is not autoconf based, so we use the
# generic-package infrastructure
define BATOCERA_STELLA_CONFIGURE_CMDS
	(cd $(@D); \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		./configure $(BATOCERA_STELLA_CONF_OPTS) \
	)
endef

define BATOCERA_STELLA_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define BATOCERA_STELLA_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) DESTDIR="$(TARGET_DIR)" -C $(@D) install
endef

$(eval $(generic-package))
