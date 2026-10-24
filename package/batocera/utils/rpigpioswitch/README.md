# Argon ONE profiles

Select `ARGONONE` through `S92switch setup`, or configure:

```ini
system.power.switch=ARGONONE
system.argonone.profile=auto
```

Set the profile explicitly in `/userdata/system/batocera.conf` when needed:

| Profile | Intended hardware | Fan and power control |
| --- | --- | --- |
| `auto` | Existing Pi 4/Pi 5 configurations | Pi 4 (`bcm2711`) selects `legacy`; Pi 5 (`bcm2712`) selects `register` |
| `legacy` | Argon ONE V1, V2 and M.2 cases using the original protocol | Single-byte fan commands and `0xff` shutdown |
| `register` | Argon ONE V3 or firmware supporting control registers | Fan register `0x80`; shutdown register `0x86`, value `1` |
| `native` | Argon ONE V5 with Raspberry Pi 5 | Kernel PWM fan control and Batocera's native power-button handling |

`auto` selects the established architecture defaults. It does **not** identify the case or probe firmware. A Pi 5 with a V5 requires `system.argonone.profile=native`. Explicit I2C profiles can override the architecture default when a case firmware requires the other protocol.

After changing profiles, restart `/etc/init.d/S92switch` or reboot. The launcher remembers the startup profile in `/var/run/argonone.profile`, so stopping the existing daemon still uses the correct protocol after a configuration edit. Native mode bypasses I2C/UART boot configuration and does not start an Argon daemon or take control of GPIO4.

## I2C profiles

The startup configuration enables the required I2C/UART settings. A reboot may be necessary when enabling support for the first time. UART must remain enabled so the case can detect completed OS shutdown before cutting power.

Temperature mappings remain in `/userdata/system/configs/argonone.conf`, one Celsius threshold and percentage per line:

```ini
55=30
60=55
65=100
```

Button monitoring identifies the header GPIO controller by pinctrl identity and its `GPIO4` line, rather than assuming a `/dev/gpiochip` number. It measures high pulses using kernel edge timestamps: 20–30 ms exits the running emulator (or requests reboot when the script's `FORCE_REBOOT` is set to `1`); 40–50 ms requests graceful Batocera shutdown. Other pulse widths and incomplete/lost edge pairs are ignored. The shutdown hook sends the case's power-cut signal; the button handler does not cut power directly.

If GPIO discovery or access fails, the error is reported and fan control continues. Check the service output if the button does not work.

## Native V5 profile

V5 uses the Raspberry Pi 5 fan connector and native power-button hardware. Linux manages the fan curve, and Batocera's existing `KEY_POWER` mapping requests shutdown. This profile does not apply `argonone.conf`, `FORCE_REBOOT`, or I2C case commands. Native thermal settings use the Pi 5's `fan_temp*` boot parameters instead.

## Validation and scope

These profiles implement the documented mechanisms for the listed families, including storage variants that use the same controller. They do not assert compatibility with every hardware or firmware revision. Storage, audio, IR and optional displays are outside this fan/button/power change.

Tests simulate both I2C protocols, GPIO identities and pulse events, native actions without hardware libraries, and launcher actions against temporary boot/runtime files:

```sh
python3 -m unittest discover -s package/batocera/utils/rpigpioswitch/tests -v
```

An initial smoke check installed this controller and the Argon launcher changes on an Argon ONE M.2 with Pi 4 running Batocera 43.1. All 30 tests passed on its Python 3.12. The MCU accepted fan writes at 100% and 30%, the user's curve was restored, and the fan thread and GPIO4 BOTH-edge listener remained active with no logged errors. Boot settings, the fan curve and the saved overlay were unchanged. The user subsequently reported that both physical button tests passed: double-click emulator exit and button-initiated shutdown. Reboot behavior and physical RPM measurement remain untested; shutdown timing and filesystem cleanliness were not independently inspected. V3/V5 hardware validation, each firmware's pulse timing and a full image build remain pending.

Protocol references: [Argon40 register helper](https://github.com/Argon40Tech/Argon40case/blob/master/src/scripts/argonregister.py), [Argon40 button implementation](https://github.com/Argon40Tech/Argon40case/blob/master/src/scripts/argonpowerbutton-libgpiod.py), [V5 manual](https://argon40.com/blogs/argon-resources/argon-one-v5-case-for-raspberry-pi-5-instruction-manual), and [Batocera's native power-key mapping](https://github.com/batocera-linux/batocera.linux/blob/master/package/batocera/core/batocera-triggerhappy/conf/multimedia_keys.conf).
