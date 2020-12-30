################################################################################
#
# pm_utils
#
################################################################################

PM_UTILS_VERSION = pm-utils-1.4.1
PM_UTILS_SITE = $(call github,freedesktop,pm-utils,$(PM_UTILS_VERSION))

define PM_UTILS_AUTOGEN
    cd $(@D); ./autogen.sh
endef

PM_UTILS_PRE_CONFIGURE_HOOKS += PM_UTILS_AUTOGEN

$(eval $(autotools-package))
