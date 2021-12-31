## Directory navigation

 - `boot` These are the makefiles for building the boot partition. Usually just a manner of copying files over from the below directory, but sometimes require a bit more complex instructions.
 - `controllers` Support for extraneous controllers that EmulationStation/Batocera can't recognize by default.
 - `core` The "meat and potatoes" of Batocera. This contains most "batocera-<X>" packages, such as the config generators, ES system configurations, system utilities, splash, etc.
 - `emulators` Contains the makefiles and `git` information required for including [emulators](https://wiki.batocera.org/systems) in Batocera. This is the preferred location to apply per-emulator [patches](https://wiki.batocera.org/coding_rules#patches).
 - `gpu` Graphics drivers for all the possible hardware supported by Batocera that aren't already included in the Linux kernel by default.
 - `network` Network adapter drivers that aren't already included in the Linux kernel by default.
 - `ports` Contains the makefiles and `git` information required for including [ports](https://wiki.batocera.org/systems#port) in Batocera. This is the preferred location to apply per-port [patches](https://wiki.batocera.org/coding_rules#patches).
 - `utils` Various utilities used by Batocera, such as [case support](https://wiki.batocera.org/add_powerdevices_rpi_only), [Syncthing](https://wiki.batocera.org/syncthing), [batocera-steam](https://wiki.batocera.org/systems:steam), etc.
