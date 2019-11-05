################################################################################
#
# tzdata
#
################################################################################

TZDATA_VERSION = 2019c
TZDATA_SOURCE = tzdata$(TZDATA_VERSION).tar.gz
TZDATA_SITE = https://www.iana.org/time-zones/repository/releases
TZDATA_STRIP_COMPONENTS = 0
TZDATA_DEPENDENCIES = host-tzdata
HOST_TZDATA_DEPENDENCIES = host-zic
TZDATA_LICENSE = Public domain
HOST_TZDATA_LICENSE_FILES = LICENSE

# Take care when re-ordering this list since this might break zone
# dependencies
TZDATA_DEFAULT_ZONELIST = \
	africa antarctica asia australasia europe northamerica \
	southamerica pacificnew etcetera backward systemv factory

ifeq ($(call qstrip,$(BR2_TARGET_TZ_ZONELIST)),default)
TZDATA_ZONELIST = $(TZDATA_DEFAULT_ZONELIST)
else
TZDATA_ZONELIST = $(call qstrip,$(BR2_TARGET_TZ_ZONELIST))
endif

TZDATA_LOCALTIME = $(call qstrip,$(BR2_TARGET_LOCALTIME))

# No need to extract for target, we're using the host-installed files
TZDATA_EXTRACT_CMDS =

define TZDATA_INSTALL_TARGET_CMDS
	$(INSTALL) -d -m 0755 $(TARGET_DIR)/usr/share/zoneinfo
	cp -a $(HOST_DIR)/share/zoneinfo/* $(TARGET_DIR)/usr/share/zoneinfo
	cd $(TARGET_DIR)/usr/share/zoneinfo; \
	for zone in posix/*; do \
	    ln -sfn "$${zone}" "$${zone##*/}"; \
	done
	if [ ! -f $(TARGET_DIR)/usr/share/zoneinfo/$(TZDATA_LOCALTIME) ]; then \
		printf "Error: '%s' is not a valid timezone, check your BR2_TARGET_LOCALTIME setting\n" \
			"$(TZDATA_LOCALTIME)"; \
		exit 1; \
	fi
	ln -sf ../usr/share/zoneinfo/$(TZDATA_LOCALTIME) $(TARGET_DIR)/etc/localtime
	echo "$(TZDATA_LOCALTIME)" >$(TARGET_DIR)/etc/timezone
endef

define HOST_TZDATA_BUILD_CMDS
	(cd $(@D); \
		for zone in $(TZDATA_ZONELIST); do \
			$(ZIC) -d _output/posix -y yearistype.sh $$zone || exit 1; \
			$(ZIC) -d _output/right -L leapseconds -y yearistype.sh $$zone || exit 1; \
		done; \
	)
endef

define HOST_TZDATA_INSTALL_CMDS
	$(INSTALL) -d -m 0755 $(HOST_DIR)/share/zoneinfo
	cp -a $(@D)/_output/* $(@D)/*.tab $(HOST_DIR)/share/zoneinfo
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
