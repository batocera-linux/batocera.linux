## Directory navigation

 - `configgen` Go here for the generators themselves.
 - `configs` A set of default settings, for both global and per-platform. If defining a new emulator/system, it will need to be defined in [configgen-defaults](https://github.com/batocera-linux/batocera.linux/blob/master/package/batocera/core/batocera-configgen/configs/configgen-defaults.yml).
 - `datainit` Some extraneous files required for emulators.

### Using emulatorlauncher on debian based systems

To use `emulatorlauncher` on debian based system, you can `python setup.py install` it with the following python dependencies :  

```
sudo apt install python3-yaml python3-evdev python3-pil python3-psutil python3-httplib2
```
