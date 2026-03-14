################################################################################
#
# batocera-es-system
#
################################################################################

BATOCERA_ES_SYSTEM_SOURCE=
BATOCERA_ES_SYSTEM_OVERRIDE_SRCDIR=
BATOCERA_ES_SYSTEM_INSTALL_STAGING = YES
BATOCERA_ES_SYSTEM_DEPENDENCIES = host-batocera-es-system batocera-configgen host-gettext

HOST_BATOCERA_ES_SYSTEM_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/python-src/batocera-es-system
HOST_BATOCERA_ES_SYSTEM_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"
HOST_BATOCERA_ES_SYSTEM_SOURCE=
HOST_BATOCERA_ES_SYSTEM_SETUP_TYPE=hatch
HOST_BATOCERA_ES_SYSTEM_DEPENDENCIES = host-python-pyyaml host-python-ruamel-yaml host-python-typing-extensions

$(eval $(call register,_shared.emulator.yml _global.emulator.yml lexaloffle.emulator.yml sh.emulator.yml))
$(eval $(call register-if-kconfig,BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY,tdp._shared.emulator.yml))
$(eval $(call register-if-none-of,$(BATOCERA_SYSTEM_ARCH),s905 bcm2835 bcm2836,hud._shared.emulator.yml))
$(eval $(call register-if-kconfig,BR2_PACKAGE_STELLA,stella.emulator.yml))

define BATOCERA_ES_SYSTEM_EXTRACT_CMDS
	mkdir -p $(BATOCERA_ES_SYSTEM_DIR)/roms

	mkdir -p $(BATOCERA_ES_SYSTEM_DIR)/locales
	cp -pr $(BATOCERA_ES_SYSTEM_PKGDIR)/locales $(BATOCERA_ES_SYSTEM_DIR)
endef

define BATOCERA_ES_SYSTEM_BUILD_CMDS
	@echo '$(EMULATOR_INFO_PATHS)' > $(BATOCERA_ES_SYSTEM_DIR)/info_files.txt
	$(HOST_DIR)/bin/batocera-build-es-data \
		--es-systems-yml=$(BATOCERA_ES_SYSTEM_PKGDIR)/es_systems.yml \
		--locales-dir=$(BATOCERA_ES_SYSTEM_PKGDIR)/locales \
		--roms-dir=$(BATOCERA_ES_SYSTEM_PKGDIR)/roms \
		--configgen=$(STAGING_DIR)/usr/share/batocera/configgen \
		--keys-dir=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera \
		--output=$(BATOCERA_ES_SYSTEM_DIR) \
		--arch=$(BATOCERA_SYSTEM_ARCH) \
		$(BATOCERA_ES_SYSTEM_DIR)/info_files.txt

	$(call BATOCERA_ES_SYSTEM_BUILD_PO_FILES,$(BATOCERA_ES_SYSTEM_DIR),$(BATOCERA_ES_SYSTEM_DIR)/locales)
endef

# This is defined as a macro so it can be reused in both build and update-locale-po-files
define BATOCERA_ES_SYSTEM_BUILD_PO_FILES
	# translations
	mkdir -p $(2)
	(echo "$(1)/es_external_translations.h"; echo "$(1)/es_keys_translations.h") | \
		xgettext --language=C --add-comments=TRANSLATION -f - -o \
		$(2)/batocera-es-system.pot --no-location --keyword=_

	# remove the pot creation date always changing
	sed -i '/^"POT-Creation-Date: /d' $(2)/batocera-es-system.pot

	# Merge translations and validate them
	for PO in $(2)/*/batocera-es-system.po; do \
		(LANG=C msgmerge -s -U --no-fuzzy-matching $${PO} $(2)/batocera-es-system.pot && \
		printf "%s " $$(basename $$(dirname $${PO})) && \
		LANG=C msgfmt -o /dev/null $${PO} --statistics) || exit 1; \
	done
endef

define BATOCERA_ES_SYSTEM_INSTALL_STAGING_CMDS
 	$(INSTALL) -m 0644 -D $(@D)/es_external_translations.h $(STAGING_DIR)/usr/share/batocera-es-system/es_external_translations.h
 	$(INSTALL) -m 0644 -D $(@D)/es_keys_translations.h $(STAGING_DIR)/usr/share/batocera-es-system/es_keys_translations.h
	cp -pr $(@D)/locales $(STAGING_DIR)/usr/share/batocera-es-system
endef

define BATOCERA_ES_SYSTEM_INSTALL_TARGET_CMDS
 	$(INSTALL) -m 0644 -D $(@D)/es_systems.cfg $(TARGET_DIR)/usr/share/emulationstation/es_systems.cfg
 	$(INSTALL) -m 0644 -D $(@D)/es_features.cfg $(TARGET_DIR)/usr/share/emulationstation/es_features.cfg
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit
	mkdir -p $(@D)/roms  # in case there is no rom
	cp -pr $(@D)/roms $(TARGET_DIR)/usr/share/batocera/datainit/
endef

$(eval $(generic-package))
$(eval $(host-python-package))
$(eval $(emulator-info-package))
