################################################################################
#
# libretro-scummvm
#
################################################################################
# Version: Commits on Sep 15, 2026 (check - LIBRETRO_SCUMMVM_DEPS)
LIBRETRO_SCUMMVM_VERSION = 430653b98d75e86d15a293c0aa3b3dbed56b499d
LIBRETRO_SCUMMVM_SITE = $(call github,libretro,scummvm,$(LIBRETRO_SCUMMVM_VERSION))
LIBRETRO_SCUMMVM_LICENSE = GPLv2
LIBRETRO_SCUMMVM_DEPENDENCIES += retroarch host-zip
LIBRETRO_SCUMMVM_EMULATOR_INFO = scummvm.libretro.core.yml

# the fork ships mm.dat 1.2 while xeen expects 1.3, scummvm regenerated it upstream
LIBRETRO_SCUMMVM_MM_DAT_COMMIT = 5dbac90a649413207ae8fc67071fe3f1d77b7603
LIBRETRO_SCUMMVM_EXTRA_DOWNLOADS = \
    https://raw.githubusercontent.com/scummvm/scummvm/$(LIBRETRO_SCUMMVM_MM_DAT_COMMIT)/dists/engine-data/mm.dat

LIBRETRO_SCUMMVM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi5_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_SCUMMVM_PLATFORM = armv cortexa9 neon hardfloat
else ifeq ($(BR2_aarch64)$(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
LIBRETRO_SCUMMVM_PLATFORM = unix
LIBRETRO_SCUMMVM_MAKE_OPTS += TARGET_64BIT=1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110),y)
LIBRETRO_SCUMMVM_PLATFORM = unix
LIBRETRO_SCUMMVM_MAKE_OPTS += TARGET_64BIT=1 fpic=1
LIBRETRO_SCUMMVM_CONF_OPTS += CXXFLAGS="$(TARGET_CXXFLAGS) -fPIC -O1"
LIBRETRO_SCUMMVM_CONF_OPTS += CFLAGS="$(TARGET_CFLAGS) -fPIC -O1"
LIBRETRO_SCUMMVM_CONF_OPTS += LDFLAGS="$(TARGET_LDFLAGS) -shared -fPIC"
endif

# match the retroarch GL flavour, a desktop GL context request fails on GLES builds
ifneq ($(BR2_x86_64),y)
ifeq ($(BR2_PACKAGE_BATOCERA_GLES3)$(BR2_PACKAGE_BATOCERA_GLES2),y)
LIBRETRO_SCUMMVM_MAKE_OPTS += FORCE_OPENGLES2=1
endif
endif

define LIBRETRO_CLONE_AND_INIT
	mkdir -p $(@D)/backends/platform/libretro/deps/$(1)
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) init
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) remote add origin https://github.com/libretro/$(1)
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) fetch --depth 1 origin $(2)
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) checkout FETCH_HEAD
	$(BR2_GIT) -C $(@D)/backends/platform/libretro/deps/$(1) submodule update --init --recursive --depth 1
endef

# Details from backends/platform/libretro/dependencies.mk
define LIBRETRO_SCUMMVM_DEPS
	$(call LIBRETRO_CLONE_AND_INIT,libretro-deps,bab7d258c451c0e7cba4b6a79f1b062c13efff38)
	$(call LIBRETRO_CLONE_AND_INIT,libretro-common,879c8d507b0b52e77e27d759239c2b5df1e26dfd)
endef

define LIBRETRO_SCUMMVM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/backends/platform/libretro \
        platform="$(LIBRETRO_SCUMMVM_PLATFORM)" $(LIBRETRO_SCUMMVM_MAKE_OPTS) \
		$(LIBRETRO_SCUMMVM_CONF_OPTS)
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/backends/platform/libretro \
		platform="$(LIBRETRO_SCUMMVM_PLATFORM)" datafiles
	$(UNZIP) -o $(@D)/backends/platform/libretro/scummvm.zip \
		-d $(@D)/backends/platform/libretro
endef

define LIBRETRO_SCUMMVM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/backends/platform/libretro/scummvm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/scummvm_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/libretro-scummvm
	cp -r $(@D)/backends/platform/libretro/scummvm/. \
		$(TARGET_DIR)/usr/share/libretro-scummvm/
endef

define LIBRETRO_SCUMMVM_UPDATE_MM_DAT
	cp $(LIBRETRO_SCUMMVM_DL_DIR)/mm.dat $(@D)/dists/engine-data/mm.dat
endef

LIBRETRO_SCUMMVM_POST_EXTRACT_HOOKS += LIBRETRO_SCUMMVM_UPDATE_MM_DAT

# workaround script issue
LIBRETRO_SCUMMVM_PRE_CONFIGURE_HOOKS += LIBRETRO_SCUMMVM_DEPS

$(eval $(generic-package))
$(eval $(emulator-info-package))
