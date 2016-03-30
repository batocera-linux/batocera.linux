################################################################################
#
# p7zip
#
################################################################################
P7ZIP_VERSION = 15.14.1
P7ZIP_SOURCE = p7zip_${P7ZIP_VERSION}_src_all.tar.bz2
# Author wrongly inserted a space in the folder version...
P7ZIP_SITE = http://downloads.sourceforge.net/project/p7zip/p7zip/15.14%20.1
P7ZIP_LICENCE = LGPLv2
# http://buildroot-busybox.2317881.n4.nabble.com/PATCH-v2-p7zip-light-new-package-td9305.html

define P7ZIP_BUILD_CMDS 
	sed -i -e "s|CC=.*|CC=$(TARGET_CC) \$$(ALLFLAGS)|" -e "s|CXX=.*|CXX=$(TARGET_CXX) \$$(ALLFLAGS)|" $(@D)/makefile.machine 
	$(MAKE) -C $(@D) 7z
endef 

define P7ZIP_INSTALL_TARGET_CMDS 
	(cd $(@D); DEST_HOME=$(TARGET_DIR)/usr ./install.sh)
endef 
 
define P7ZIP_UNINSTALL_TARGET_CMDS 
	rm -f $(TARGET_DIR)/usr/bin/7z{,a,r} 
	rm -rf $(TARGET_DIR)/usr/lib/p7zip 
endef 
 
$(eval $(generic-package)) 
