################################################################################
#
# BATOCERA-ES-SYSTEM
#
################################################################################

BATOCERA_ES_SYSTEM_DEPENDENCIES = host-python3 host-python-pyyaml batocera-configgen host-gettext
BATOCERA_ES_SYSTEM_SOURCE=
BATOCERA_ES_SYSTEM_VERSION=1.03

define BATOCERA_ES_SYSTEM_BUILD_CMDS
	$(HOST_DIR)/bin/python \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/batocera-es-system.py \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/es_systems.yml        \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/es_features.yml       \
		$(@D)/es_external_translations.h \
		$(@D)/es_keys_translations.h \
                $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales/blacklisted-words.txt \
		$(CONFIG_DIR)/.config \
		$(@D)/es_systems.cfg \
		$(@D)/es_features.cfg \
		$(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml \
		$(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/roms \
		$(@D)/roms $(BATOCERA_SYSTEM_ARCH)
		# translations
		mkdir -p $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales
		(echo "$(@D)/es_external_translations.h"; echo "$(@D)/es_keys_translations.h") | xgettext --language=C --add-comments=TRANSLATION -f - -o $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales/batocera-es-system.pot --no-location --keyword=_
		# remove the pot creation date always changing
		sed -i '/^"POT-Creation-Date: /d' $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales/batocera-es-system.pot

		for PO in $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales/*/batocera-es-system.po; do (msgmerge -U --no-fuzzy-matching $${PO} $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales/batocera-es-system.pot && printf "%s " $$(basename $$(dirname $${PO})) && LANG=C msgfmt -o /dev/null $${PO} --statistics) || exit 1; done

		# install staging
		mkdir -p $(STAGING_DIR)/usr/share/batocera-es-system/locales
		cp $(@D)/es_external_translations.h      $(STAGING_DIR)/usr/share/batocera-es-system/
		cp $(@D)/es_keys_translations.h          $(STAGING_DIR)/usr/share/batocera-es-system/
		cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/locales $(STAGING_DIR)/usr/share/batocera-es-system
endef

define BATOCERA_ES_SYSTEM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit
	$(INSTALL) -m 0644 -D $(@D)/es_systems.cfg $(TARGET_DIR)/usr/share/emulationstation/es_systems.cfg
	$(INSTALL) -m 0644 -D $(@D)/es_features.cfg $(TARGET_DIR)/usr/share/emulationstation/es_features.cfg
	mkdir -p $(@D)/roms # in case there is no rom
	cp -pr $(@D)/roms $(TARGET_DIR)/usr/share/batocera/datainit/
endef

$(eval $(generic-package))
