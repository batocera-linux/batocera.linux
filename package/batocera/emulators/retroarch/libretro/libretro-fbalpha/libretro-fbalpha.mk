################################################################################
#
# FBALPHA
#
################################################################################
# Version.: Commits on Apr 30, 2021
LIBRETRO_FBALPHA_VERSION = 0a25932ac981108a5eb5ef401056ac78ea57e3ce
LIBRETRO_FBALPHA_SITE = $(call github,libretro,fbalpha,$(LIBRETRO_FBALPHA_VERSION))
LIBRETRO_FBALPHA_LICENSE = Non-commercial

define LIBRETRO_FBALPHA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FBALPHA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fbalpha_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fbalpha_libretro.so

    # Bios
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/fbalpha/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/fbalpha

    # Need to think of another way to use these files.
    # They take up a lot of space on tmpfs.
	$(INSTALL) -D $(@D)/dats/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/fbalpha
endef

$(eval $(generic-package))
