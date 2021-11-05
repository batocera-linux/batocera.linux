################################################################################
#
# devilutionx
#
################################################################################

DEVILUTIONX_VERSION = cda80688e7353b0e8628cdf919586dc6be60cc7f
DEVILUTIONX_SITE = $(call github,diasurgical,devilutionx,$(DEVILUTIONX_VERSION))
DEVILUTIONX_DEPENDENCIES = sdl2 sdl2_image fmt libsodium host-gettext host-smpq

DEVILUTIONX_PKG_DIR = $(TARGET_DIR)/opt/retrolx/devilutionx
DEVILUTIONX_PKG_INSTALL_DIR = /userdata/packages/$(RETROLX_SYSTEM_ARCH)/devilutionx

# Prefill the player name when creating a new character, in case the device does
# not have a keyboard.
DEVILUTIONX_CONF_OPTS += -DPREFILL_PLAYER_NAME=ON

# Define VERSION_NUM so that DevilutionX build does not attempt to get it from
# git, to which it doesn't have access here.
#
# VERSION_NUM must match (\d\.)*\d. If the DEVILUTIONX_VERSION does not
# match this pattern (tested by simply looking for a "."), we use a fixed
# version with a commit hash suffix instead.
ifeq ($(findstring .,$(DEVILUTIONX_VERSION)),.)
DEVILUTIONX_CONF_OPTS += -DVERSION_NUM=$(DEVILUTIONX_VERSION)
else
DEVILUTIONX_CONF_OPTS += -DVERSION_NUM=1.3.0 -DVERSION_SUFFIX="-$(DEVILUTIONX_VERSION)"
endif

# Vendored dependencies (in DevilutionX they're fetched via CMake's FetchContent).
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_FULLY_DISCONNECTED=ON

# https://github.com/diasurgical/devilutionX/blob/1.3.0/3rdParty/SDL_audiolib/CMakeLists.txt
DEVILUTIONX_SDL_AUDIOLIB_VERSION = aa79660eba4467a44f9dcaecf26b0f0a000abfd7
DEVILUTIONX_SDL_AUDIOLIB_SOURCE = $(DEVILUTIONX_SDL_AUDIOLIB_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,realnc,SDL_audiolib,$(DEVILUTIONX_SDL_AUDIOLIB_SOURCE))
define DEVILUTIONX_SDL_AUDIOLIB_EXTRACT
	mkdir -p $(@D)/br-fetched/SDL_audiolib-$(DEVILUTIONX_SDL_AUDIOLIB_VERSION)
	$(call suitable-extractor,$(DEVILUTIONX_SDL_AUDIOLIB_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_SDL_AUDIOLIB_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/SDL_audiolib-$(DEVILUTIONX_SDL_AUDIOLIB_VERSION) $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_SDL_AUDIOLIB_EXTRACT
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_SOURCE_DIR_SDL_AUDIOLIB=$(DEVILUTIONX_BUILDDIR)br-fetched/SDL_audiolib-$(DEVILUTIONX_SDL_AUDIOLIB_VERSION)

# https://github.com/diasurgical/devilutionX/blob/1.3.0/3rdParty/simpleini/CMakeLists.txt
DEVILUTIONX_SIMPLEINI_VERSION = 7bca74f6535a37846162383e52071f380c99a43a
DEVILUTIONX_SIMPLEINI_SOURCE = $(DEVILUTIONX_SIMPLEINI_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,brofield,simpleini,$(DEVILUTIONX_SIMPLEINI_SOURCE))
define DEVILUTIONX_SIMPLEINI_EXTRACT
	mkdir -p $(@D)/br-fetched/simpleini-$(DEVILUTIONX_SIMPLEINI_VERSION)
	$(call suitable-extractor,$(DEVILUTIONX_SIMPLEINI_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_SIMPLEINI_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/simpleini-$(DEVILUTIONX_SIMPLEINI_VERSION) $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_SIMPLEINI_EXTRACT
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_SOURCE_DIR_SIMPLEINI=$(DEVILUTIONX_BUILDDIR)br-fetched/simpleini-$(DEVILUTIONX_SIMPLEINI_VERSION)

# https://github.com/diasurgical/devilutionX/blob/1.3.0/3rdParty/asio/CMakeLists.txt
DEVILUTIONX_ASIO_VERSION = ebeff99f539da23d27c2e8d4bdbc1ee011968644
DEVILUTIONX_ASIO_SOURCE = $(DEVILUTIONX_ASIO_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,diasurgical,asio,$(DEVILUTIONX_ASIO_SOURCE))
define DEVILUTIONX_ASIO_EXTRACT
	mkdir -p $(@D)/br-fetched/asio-$(DEVILUTIONX_ASIO_VERSION)
	$(call suitable-extractor,$(DEVILUTIONX_ASIO_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_ASIO_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/asio-$(DEVILUTIONX_ASIO_VERSION) $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_ASIO_EXTRACT
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_SOURCE_DIR_ASIO=$(DEVILUTIONX_BUILDDIR)br-fetched/asio-$(DEVILUTIONX_ASIO_VERSION)

# https://github.com/diasurgical/devilutionX/blob/1.3.0/3rdParty/libzt/CMakeLists.txt
DEVILUTIONX_LIBZT_VERSION = b2be9882771116fcfd4ad918f36de8587324d9e7
DEVILUTIONX_LIBZT_SOURCE = $(DEVILUTIONX_LIBZT_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,diasurgical,libzt,$(DEVILUTIONX_LIBZT_SOURCE))
define DEVILUTIONX_LIBZT_EXTRACT
	mkdir -p $(@D)/br-fetched/libzt-$(DEVILUTIONX_LIBZT_VERSION)
	$(call suitable-extractor,$(DEVILUTIONX_LIBZT_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_LIBZT_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/libzt-$(DEVILUTIONX_LIBZT_VERSION) $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_LIBZT_EXTRACT
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_SOURCE_DIR_LIBZT=$(DEVILUTIONX_BUILDDIR)br-fetched/libzt-$(DEVILUTIONX_LIBZT_VERSION)

# libzt itself has submodules that we need to download as well:
# https://github.com/diasurgical/libzt/tree/b2be9882771116fcfd4ad918f36de8587324d9e7/.gitmodules

# https://github.com/diasurgical/libzt/tree/b2be9882771116fcfd4ad918f36de8587324d9e7/ext
DEVILUTIONX_LIBZT_ZERO_TIER_ONE_VERSION = b1350ac91118d1bd6bb71c0c41be5f4a30196838
DEVILUTIONX_LIBZT_ZERO_TIER_ONE_SOURCE = $(DEVILUTIONX_LIBZT_ZERO_TIER_ONE_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,diasurgical,ZeroTierOne,$(DEVILUTIONX_LIBZT_ZERO_TIER_ONE_SOURCE))
define DEVILUTIONX_LIBZT_ZERO_TIER_ONE_EXTRACT
	$(call suitable-extractor,$(DEVILUTIONX_LIBZT_ZERO_TIER_ONE_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_LIBZT_ZERO_TIER_ONE_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/libzt-$(DEVILUTIONX_LIBZT_VERSION)/ext/ZeroTierOne $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_LIBZT_ZERO_TIER_ONE_EXTRACT

# https://github.com/diasurgical/libzt/tree/b2be9882771116fcfd4ad918f36de8587324d9e7/ext
DEVILUTIONX_LIBZT_LWIP_VERSION = 1bf7e011caf4e992ad139f6cb8c9818a9c1fbe1b
DEVILUTIONX_LIBZT_LWIP_SOURCE = $(DEVILUTIONX_LIBZT_LWIP_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,diasurgical,lwip,$(DEVILUTIONX_LIBZT_LWIP_SOURCE))
define DEVILUTIONX_LIBZT_LWIP_EXTRACT
	$(call suitable-extractor,$(DEVILUTIONX_LIBZT_LWIP_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_LIBZT_LWIP_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/libzt-$(DEVILUTIONX_LIBZT_VERSION)/ext/lwip $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_LIBZT_LWIP_EXTRACT

# https://github.com/diasurgical/libzt/tree/b2be9882771116fcfd4ad918f36de8587324d9e7/ext
DEVILUTIONX_LIBZT_LWIP_CONTRIB_VERSION = 1f9e26e221a41542563834222c4ec8399be1908f
DEVILUTIONX_LIBZT_LWIP_CONTRIB_SOURCE = $(DEVILUTIONX_LIBZT_LWIP_CONTRIB_VERSION).tar.gz
DEVILUTIONX_EXTRA_DOWNLOADS += $(call github,diasurgical,lwip-contrib,$(DEVILUTIONX_LIBZT_LWIP_CONTRIB_SOURCE))
define DEVILUTIONX_LIBZT_LWIP_CONTRIB_EXTRACT
	$(call suitable-extractor,$(DEVILUTIONX_LIBZT_LWIP_CONTRIB_SOURCE)) $(DEVILUTIONX_DL_DIR)/$(DEVILUTIONX_LIBZT_LWIP_CONTRIB_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/br-fetched/libzt-$(DEVILUTIONX_LIBZT_VERSION)/ext/lwip-contrib $(TAR_OPTIONS) -
endef
DEVILUTIONX_POST_EXTRACT_HOOKS += DEVILUTIONX_LIBZT_LWIP_CONTRIB_EXTRACT


define DEVILUTIONX_INSTALL_TARGET_CMDS
# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/devilutionx/devilutionx.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
