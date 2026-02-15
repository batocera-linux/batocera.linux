################################################################################
#
# xone
#
################################################################################

# Workaround the need for Kernel 5.11 or greater with some boards
ifeq ($(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_4)$(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_10),y)
    XONE_VERSION = bbf0dcc484c3f5611f4e375da43e0e0ef08f3d18
else
    XONE_VERSION = v0.5.5
endif

XONE_SITE = $(call github,dlundqvist,xone,$(XONE_VERSION))
XONE_DEPENDENCIES = host-libcurl host-cabextract libusb

XONE_FIRMWARE_URLS = \
https://catalog.s.download.windowsupdate.com/d/msdownload/update/driver/drvs/2017/03/2ea9591b-f751-442c-80ce-8f4692cdc67b_6b555a3a288153cf04aec6e03cba360afe2fce34.cab \
https://catalog.s.download.windowsupdate.com/c/msdownload/update/driver/drvs/2017/07/1cd6a87c-623f-4407-a52d-c31be49e925c_e19f60808bdcbfbd3c3df6be3e71ffc52e43261e.cab \
https://catalog.s.download.windowsupdate.com/c/msdownload/update/driver/drvs/2017/06/1dbd7cb4-53bc-4857-a5b0-5955c8acaf71_9081931e7d664429a93ffda0db41b7545b7ac257.cab \
https://catalog.s.download.windowsupdate.com/d/msdownload/update/driver/drvs/2017/08/aeff215c-3bc4-4d36-a3ea-e14bfa8fa9d2_e58550c4f74a27e51e5cb6868b10ff633fa77164.cab

XONE_FIRMWARE_PIDS = 02e6 02fe 02f9 091e

XONE_FIRMWARE_FILENAMES = FW_ACC_00U.bin FW_ACC_00U.bin FW_ACC_CL.bin FW_ACC_BR.bin

XONE_FIRMWARE_HASHES = \
080ce4091e53a4ef3e5fe29939f51fd91f46d6a88be6d67eb6e99a5723b3a223 \
48084d9fa53b9bb04358f3bb127b7495dc8f7bb0b3ca1437bd24ef2b6eabdf66 \
0023a7bae02974834500c665a281e25b1ba52c9226c84989f9084fa5ce591d9b \
e2710daf81e7b36d35985348f68a81d18bc537a2b0c508ffdfde6ac3eae1bad7

define XONE_PREPARE_FIRMWARE
	FIRMWARE_STAGING_DIR="$(@D)/firmware_files"; \
	mkdir -p "$$FIRMWARE_STAGING_DIR"; \
	i=1; \
	for URL in $(XONE_FIRMWARE_URLS); do \
		PID=`printf '%s' "$(XONE_FIRMWARE_PIDS)" | tr ' ' '\n' | sed -n "$$i"p`; \
		FILENAME=`printf '%s' "$(XONE_FIRMWARE_FILENAMES)" | tr ' ' '\n' | sed -n "$$i"p`; \
		HASH=`printf '%s' "$(XONE_FIRMWARE_HASHES)" | tr ' ' '\n' | sed -n "$$i"p`; \
		PID=$$(echo "$$PID" | tr -d '[:space:]'); \
		FILENAME=$$(echo "$$FILENAME" | tr -d '[:space:]'); \
		HASH=$$(echo "$$HASH" | tr -d '[:space:]'); \
		echo "--> Preparing firmware PID=$$PID ($$FILENAME)"; \
		TEMP_CAB="$(@D)/driver_$$i.cab"; \
		TEMP_EXTRACT_DIR="$(@D)/extract_$$i"; \
		DEST_NAME="xone_dongle_$$PID.bin"; \
		if ! wget -c --tries=3 --trust-server-names -O "$$TEMP_CAB" "$$URL"; then \
			echo "WARNING: Failed to download $$URL, skipping"; \
			i=`expr $$i + 1`; \
			continue; \
		fi; \
		mkdir -p "$$TEMP_EXTRACT_DIR"; \
		$(HOST_DIR)/bin/cabextract -d "$$TEMP_EXTRACT_DIR" "$$TEMP_CAB"; \
		if [ -f "$$TEMP_EXTRACT_DIR/$$FILENAME" ]; then \
			echo "$$HASH  $$TEMP_EXTRACT_DIR/$$FILENAME" | sha256sum -c -; \
			mv "$$TEMP_EXTRACT_DIR/$$FILENAME" "$$FIRMWARE_STAGING_DIR/$$DEST_NAME"; \
			echo "--- Staged $$DEST_NAME ---"; \
		else \
			echo "WARNING: $$FILENAME not found in CAB $$TEMP_CAB"; \
		fi; \
		rm -rf "$$TEMP_EXTRACT_DIR" "$$TEMP_CAB"; \
		i=`expr $$i + 1`; \
	done
endef

XONE_PRE_INSTALL_TARGET_HOOKS += XONE_PREPARE_FIRMWARE

define XONE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/modprobe.d
	$(INSTALL) -D -m 0644 \
		$(@D)/install/modprobe.conf \
		$(TARGET_DIR)/etc/modprobe.d/xone-blacklist.conf
	mkdir -p $(TARGET_DIR)/lib/firmware
	cp -a $(@D)/firmware_files/. $(TARGET_DIR)/lib/firmware/
endef

$(eval $(kernel-module))
$(eval $(generic-package))
