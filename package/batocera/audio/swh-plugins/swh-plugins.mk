################################################################################
#
# swh-plugins
#
################################################################################

SWH_PLUGINS_VERSION = v0.4.17
SWH_PLUGINS_SITE = $(call github,swh,ladspa,$(SWH_PLUGINS_VERSION))
SWH_PLUGINS_LICENSE = GPL-2.0+
SWH_PLUGINS_LICENSE_FILES = COPYING
SWH_PLUGINS_DEPENDENCIES = host-libxml-parser-perl

# only the dynamics plugins, built without the autotools/gettext tree
SWH_PLUGINS_LADSPA = sc4_1882 fast_lookahead_limiter_1913

define SWH_PLUGINS_BUILD_CMDS
	touch $(@D)/config.h
	$(foreach p,$(SWH_PLUGINS_LADSPA), \
		cd $(@D) && perl ./makestub.pl $(p).xml > $(p).c$(sep))
	cd $(@D) && $(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) -fPIC -shared -I. \
		sc4_1882.c util/db.c util/rms.c -lm -o sc4_1882.so
	cd $(@D) && $(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) -fPIC -shared -I. \
		fast_lookahead_limiter_1913.c -lm -o fast_lookahead_limiter_1913.so
endef

define SWH_PLUGINS_INSTALL_TARGET_CMDS
	$(foreach p,$(SWH_PLUGINS_LADSPA), \
		$(INSTALL) -D -m 0755 $(@D)/$(p).so $(TARGET_DIR)/usr/lib/ladspa/$(p).so$(sep))
endef

$(eval $(generic-package))
