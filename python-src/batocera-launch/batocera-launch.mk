################################################################################
#
# batocera-launch
#
################################################################################

BATOCERA_LAUNCH_SETUP_TYPE=hatch
BATOCERA_LAUNCH_DEPENDENCIES = \
	python-batocera-common \
	python-uvloop \
	python-evdev \
	python-pyudev \
	python-toml \
	python-pillow \
	python-qrcode
BATOCERA_LAUNCH_INSTALL_STAGING = YES

BATOCERA_LAUNCH_LOCAL_PYTHON_EXCLUSIONS = \
	$(addprefix batocera_launch/emulators/, \
		$(if $(BR2_PACKAGE_ABUSE),,abuse.py) \
		$(if $(BR2_PACKAGE_APPLEWIN),,applewin.py) \
		$(if $(BR2_PACKAGE_AZAHAR),,azahar.py) \
		$(if $(BR2_PACKAGE_BSTONE),,bstone.py) \
		$(if $(BR2_PACKAGE_CANNONBALL),,cannonball.py) \
		$(if $(BR2_PACKAGE_CATACOMBGL),,catacombgl.py) \
		$(if $(BR2_PACKAGE_CLK),,clk.py) \
		$(if $(BR2_PACKAGE_CORSIXTH),,corsixth.py) \
		$(if $(BR2_PACKAGE_DEVILUTIONX),,devilutionx.py) \
		$(if $(BR2_PACKAGE_DHEWM3),,dhewm3.py) \
		$(if $(BR2_PACKAGE_DOSBOX),,dosbox.py) \
		$(if $(BR2_PACKAGE_DOSBOX_STAGING),,dosbox_staging.py) \
		$(if $(BR2_PACKAGE_DOSBOX_X),,dosboxx.py) \
		$(if $(BR2_PACKAGE_DXX_REBIRTH),,dxx_rebirth.py) \
		$(if $(BR2_PACKAGE_EASYRPG_PLAYER),,easyrpg.py) \
		$(if $(BR2_PACKAGE_ECWOLF),,ecwolf.py) \
		$(if $(BR2_PACKAGE_EDUKE32),,eduke32.py) \
		$(if $(BR2_PACKAGE_ETLEGACY),,etlegacy.py) \
		$(if $(BR2_PACKAGE_PIFBA),,fba2x.py) \
		$(if $(BR2_PACKAGE_FLATPAK),,flatpak.py) \
		$(if $(BR2_PACKAGE_GSPLUS),,gsplus.py) \
		$(if $(BR2_PACKAGE_HATARI),,hatari.py) \
		$(if $(BR2_PACKAGE_HCL),,hcl.py) \
		$(if $(BR2_PACKAGE_HURRICAN),,hurrican.py) \
		$(if $(BR2_PACKAGE_IKEMEN),,ikemen.py) \
		$(if $(BR2_PACKAGE_IOQUAKE3)$(BR2_PACKAGE_VKQUAKE3),,ioquake3.py) \
		$(if $(BR2_PACKAGE_IORTCW),,iortcw.py) \
		$(if $(BR2_PACKAGE_JAZZ2_NATIVE),,jazz2_native.py) \
		$(if $(BR2_PACKAGE_LIGHTSPARK),,lightspark.py) \
		$(if $(BR2_PACKAGE_NANOBOYADVANCE),,nanoboyadvance.py) \
		$(if $(BR2_PACKAGE_OD_COMMANDER),,odcommander.py) \
		$(if $(BR2_PACKAGE_BATOCERA_PYGAME),,pygame.py) \
		$(if $(BR2_PACKAGE_PYTHON_PYXEL),,pyxel.py) \
		$(if $(BR2_PACKAGE_RAZE),,raze.py) \
		$(if $(BR2_PACKAGE_REDREAM),,redream.py) \
		$(if $(BR2_PACKAGE_RUFFLE),,ruffle.py) \
		$(if $(BR2_PACKAGE_SIMCOUPE),,samcoupe.py) \
		$(if $(BR2_PACKAGE_SCUMMVM),,scummvm.py) \
		$(if $(BR2_PACKAGE_SDLPOP),,sdlpop.py) \
		$(if $(BR2_PACKAGE_SOLARUS_ENGINE),,solarus.py) \
		$(if $(BR2_PACKAGE_SONIC3_AIR),,sonic3_air.py) \
		$(if $(BR2_PACKAGE_SONIC_MANIA),,sonic_mania.py) \
		$(if $(BR2_PACKAGE_SONIC2013)$(BR2_PACKAGE_SONICCD),,sonicretro.py) \
		$(if $(BR2_PACKAGE_BATOCERA_STEAM),,steam.py) \
		$(if $(BR2_PACKAGE_STELLA),,stella.py) \
		$(if $(BR2_PACKAGE_TARADINO),,taradino.py) \
		$(if $(BR2_PACKAGE_THEFORCEENGINE),,theforceengine.py) \
		$(if $(BR2_PACKAGE_THEXTECH),,thextech.py) \
		$(if $(BR2_PACKAGE_TIC80),,tic80.py) \
		$(if $(BR2_PACKAGE_TRX),,trx.py) \
		$(if $(BR2_PACKAGE_TSUGARU),,tsugaru.py) \
		$(if $(BR2_PACKAGE_TYRIAN),,tyrian.py) \
		$(if $(BR2_PACKAGE_UQM),,uqm.py) \
		$(if $(BR2_PACKAGE_VKQUAKE),,vkquake.py) \
		$(if $(BR2_PACKAGE_VKQUAKE2),,vkquake2.py) \
		$(if $(BR2_PACKAGE_X16EMU),,x16emu.py) \
		$(if $(BR2_PACKAGE_XASH3D_FWGS),,xash3d_fwgs/) \
		$(if $(BR2_PACKAGE_XROAR),,xroar.py) \
		$(if $(BR2_PACKAGE_YQUAKE2),,yquake2.py))

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
BATOCERA_LAUNCH_ARCH = x86_64
else
BATOCERA_LAUNCH_ARCH = $(BATOCERA_ARCH)
endif

define BATOCERA_LAUNCH_INSTALL_TARGET_DEFAULT_OPTIONS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/launch/defaults
	$(INSTALL) -D -m 0644 $(@D)/resources/defaults/config.yml \
	    $(TARGET_DIR)/usr/share/batocera/launch/defaults/config.yml

	if test -e $(@D)/resources/defaults/config-$(BATOCERA_LAUNCH_ARCH).yml; then \
		$(INSTALL) -D -m 0644 $(@D)/resources/defaults/config-$(BATOCERA_LAUNCH_ARCH).yml \
		    $(TARGET_DIR)/usr/share/batocera/launch/defaults/config-arch.yml; \
	fi
endef

define BATOCERA_LAUNCH_INSTALL_STAGING_DEFAULT_OPTIONS
	mkdir -p $(STAGING_DIR)/usr/share/batocera/launch
	$(INSTALL) -D -m 0644 $(@D)/resources/defaults/config.yml \
	    $(STAGING_DIR)/usr/share/batocera/launch/defaults/config.yml

	if test -e $(@D)/resources/defaults/config-$(BATOCERA_LAUNCH_ARCH).yml; then \
		$(INSTALL) -D -m 0644 $(@D)/resources/defaults/config-$(BATOCERA_LAUNCH_ARCH).yml \
		    $(STAGING_DIR)/usr/share/batocera/launch/defaults/config-arch.yml; \
	fi
endef

define BATOCERA_LAUNCH_INSTALL_RESOURCES
	mkdir -p $(TARGET_DIR)/usr/share/batocera/launch/scripts
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	$(INSTALL) -D -m 0644 -t $(TARGET_DIR)/usr/share/batocera/launch/data \
		$(@D)/resources/data/gamesbuttonsdb.xml

	$(INSTALL) -D -m 0644 -t $(TARGET_DIR)/usr/share/batocera/launch/data/special \
		$(@D)/resources/data/special/*.toml

	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/share/batocera/launch/scripts \
		$(@D)/resources/scripts/powermode_launch_hooks.sh

	# evmapy default hotkeys file
	$(INSTALL) -D -m 0644 -t $(TARGET_DIR)/usr/share/evmapy \
		$(@D)/resources/hotkeys.keys
endef

define BATOCERA_LAUNCH_INSTALL_X86_64_SCRIPTS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/launch/scripts

	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/share/batocera/launch/scripts \
		$(@D)/resources/scripts/tdp_hooks.sh \
		$(@D)/resources/scripts/nvidia-workaround.sh
endef

BATOCERA_LAUNCH_POST_INSTALL_TARGET_HOOKS += BATOCERA_LAUNCH_INSTALL_TARGET_DEFAULT_OPTIONS
BATOCERA_LAUNCH_POST_INSTALL_TARGET_HOOKS += BATOCERA_LAUNCH_INSTALL_RESOURCES

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
BATOCERA_LAUNCH_POST_INSTALL_TARGET_HOOKS += BATOCERA_LAUNCH_INSTALL_X86_64_SCRIPTS
endif

BATOCERA_LAUNCH_POST_INSTALL_STAGING_HOOKS += BATOCERA_LAUNCH_INSTALL_STAGING_DEFAULT_OPTIONS

$(eval $(local-python-package))
