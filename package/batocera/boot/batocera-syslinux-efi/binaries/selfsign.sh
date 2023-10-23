#! /bin/bash

# https://www.rodsbooks.com/efi-bootloaders/secureboot.html#signing

# Generate a signing certificate, and use it to self-sign the x64
# bootloader.  This allows the end-user to import the certificate into
# the MOK store via mmx64.efi to bootstrap the Secure Boot flow.

# This is not run as part of the buildroot pipeline; it is included to
# document the process in case additional or updated self-signed EFI
# binaries are needed in the future.

openssl req -new -x509 -newkey rsa:2048 -keyout batocera-mok.key -out batocera-mok.crt -nodes -days 10950 -subj "/CN=Batocera.linux MOK/"
openssl x509 -in batocera-mok.crt -out batocera-mok.cer -outform DER
cp bootx64.efi /tmp/bootx64.sbat.efi
objcopy --set-section-alignment '.sbat=512' --add-section .sbat=batocera.csv --adjust-section-vma .sbat+10000000 /tmp/bootx64.sbat.efi
sbsign --key batocera-mok.key --cert batocera-mok.crt --output bootx64.selfsigned.efi /tmp/bootx64.sbat.efi
