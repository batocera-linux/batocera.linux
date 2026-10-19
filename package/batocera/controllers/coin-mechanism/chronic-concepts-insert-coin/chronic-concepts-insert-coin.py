#!/usr/bin/env python3

import time
import hid
import argparse
import sys

VENDOR_ID      = 0xc2d2
PRODUCT_ID     = 0x2727
CMD_SET_CONFIG = 0xF0
CMD_GET_CONFIG = 0xF2
REPORT_ID      = 0x00
INTERFACE_NO   = 1

HID_KEYCODES = {
  0x00: "(none)",
  0x04: "A", 0x05: "B", 0x06: "C", 0x07: "D", 0x08: "E", 0x09: "F", 0x0a: "G", 0x0b: "H", 0x0c: "I", 0x0d: "J", 0x0e: "K", 0x0f: "L", 0x10: "M",
  0x11: "N", 0x12: "O", 0x13: "P", 0x14: "Q", 0x15: "R", 0x16: "S", 0x17: "T", 0x18: "U", 0x19: "V", 0x1a: "W", 0x1b: "X", 0x1c: "Y", 0x1d: "Z",
  0x1e: "1", 0x1f: "2", 0x20: "3", 0x21: "4", 0x22: "5", 0x23: "6", 0x24: "7", 0x25: "8", 0x26: "9", 0x27: "0",
  0x28: "Enter", 0x29: "Esc", 0x2a: "Backspace", 0x2b: "Tab", 0x2c: "Space", 0x39: "Caps",
  0x3a: "F1", 0x3b: "F2", 0x3c: "F3", 0x3d: "F4",  0x3e: "F5",  0x3f: "F6", 0x40: "F7", 0x41: "F8", 0x42: "F9", 0x43: "F10", 0x44: "F11", 0x45: "F12",
}

CONFIG_LABELS = {
  "keyBtn":        "Insert Coin Button Key",
  "keyCoin":       "Coin Slot Key",
  "ssrEn":         "Button Emulation",
  "kbdEn":         "USB Keyboard Emulation",
  "piggyBank":     "Piggy Bank Mode",
  "usedBytes":     "Used Bytes",
  "totalBytes":    "Total Bytes",
  "clipCount":     "Clip Count",
  "autoPowerDown": "Auto Shutoff",
  "holdToRepeat":  "Button Hold Mode",
  "fwVersion":     "Device firmware",
  "usbPowerMode":  "USB Auto Wake and Sleep",
}

class CoinDeviceController:

  def __init__(self, vendor_id=VENDOR_ID, product_id=PRODUCT_ID, interface_no=INTERFACE_NO):
    self.vendor_id = vendor_id
    self.product_id = product_id
    self.interface_no = interface_no
    self.device = None

  def connect(self):
    target_path = None
    for device_dict in hid.enumerate(self.vendor_id, self.product_id):
      if device_dict.get("interface_number") == self.interface_no:
        target_path = device_dict["path"]
        break

    if not target_path:
      raise Exception("No device found")
      
    self.device = hid.device()
    self.device.open_path(target_path)

    print(f"Manufacturer : {self.device.get_manufacturer_string()}, Product: {self.device.get_product_string()}")

  def get_device_config(self, timeout: float = 2.0) -> dict:
    pkt = [0] * 65
    pkt[0] = REPORT_ID
    pkt[1] = CMD_GET_CONFIG

    # query reporting
    self.device.write(pkt)
    raw = self.device.read(64, timeout*1000)

    if not raw:
      raise Exception("Failed to read device")

    # decode
    used_bytes = (raw[5] << 24 | raw[6] << 16 | raw[7] << 8 | raw[8]) & 0xFFFFFFFF
    total_bytes = (
        raw[9] << 24 | raw[10] << 16 | raw[11] << 8 | raw[12]
    ) & 0xFFFFFFFF
    fw_version = (
        raw[16] << 24 | raw[17] << 16 | raw[18] << 8 | raw[19]
    ) & 0xFFFFFFFF

    return {
        "keyBtn":        raw[0],
        "keyCoin":       raw[1],
        "ssrEn":         raw[2] != 0,
        "kbdEn":         raw[3] != 0,
        "piggyBank":     raw[4] != 0,
        "usedBytes":     used_bytes,
        "totalBytes":    total_bytes,
        "clipCount":     raw[13],
        "autoPowerDown": raw[14] != 0,
        "holdToRepeat":  raw[15] != 0,
        "fwVersion":     fw_version,
        "usbPowerMode":  raw[20] != 0,
    }

  def send_config(
      self,
      config,
      keyBtn:        int = None,
      keyCoin:       int = None,
      ssrEn:         bool = None,
      kbdEn:         bool = None,
      piggyBank:     bool = None,
      autoPowerDown: bool = None,
      holdToRepeat:  bool = None,
      usbPowerMode:  bool = None,
  ):
    pkg_keyBtn        = keyBtn        if keyBtn        is not None else config["keyBtn"]
    pkg_keyCoin       = keyCoin       if keyCoin       is not None else config["keyCoin"]
    pkg_ssrEn         = ssrEn         if ssrEn         is not None else config["ssrEn"]
    pkg_kbdEn         = kbdEn         if kbdEn         is not None else config["kbdEn"]
    pkg_piggyBank     = piggyBank     if piggyBank     is not None else config["piggyBank"]
    pkg_autoPowerDown = autoPowerDown if autoPowerDown is not None else config["autoPowerDown"]
    pkg_holdToRepeat  = holdToRepeat  if holdToRepeat  is not None else config["holdToRepeat"]
    pkg_usbPowerMode  = usbPowerMode  if usbPowerMode  is not None else config["usbPowerMode"]

    buf = [0] * 64
    buf[0] = CMD_SET_CONFIG
    buf[1] = 0x00
    buf[2] = pkg_keyBtn
    buf[3] = pkg_keyCoin
    buf[4] = 0x01 if pkg_ssrEn         else 0x00
    buf[5] = 0x01 if pkg_kbdEn         else 0x00
    buf[6] = 0x01 if pkg_piggyBank     else 0x00
    buf[7] = 0x01 if pkg_autoPowerDown else 0x00
    buf[8] = 0x01 if pkg_holdToRepeat  else 0x00
    buf[9] = 0x01 if pkg_usbPowerMode  else 0x00
    self.device.write(buf)

  def close(self):
    if self.device:
      try:
        self.device.close()
      except Exception:
        pass

  def print_device_config(self, config):
    for key in [
      "keyBtn",
      "keyCoin",
      "kbdEn",
      "ssrEn",
      "piggyBank",
      "autoPowerDown",
      "holdToRepeat",
      "usbPowerMode",
      "fwVersion"
    ]:
      val = config[key]
      if key in ["keyBtn", "keyCoin"]:
        if val in HID_KEYCODES: # cases when the hardware is reconfiguring
          val = HID_KEYCODES[val]
      print(f"  {CONFIG_LABELS[key]:<24}: {val}")

def str2bool(val):
  return val == "true" or val == "1"

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--set-key-btn",         type=str, help="define key button")
  parser.add_argument("--set-key-coin",        type=str, help="define coin button")
  parser.add_argument("--set-ssr-en",          type=str, help="define button emulation")
  parser.add_argument("--set-kbd-en",          type=str, help="define keyboard emulation")
  parser.add_argument("--set-piggy-bank",      type=str, help="define piggy bank mode")
  parser.add_argument("--set-auto-power-down", type=str, help="define auto shutoff")
  parser.add_argument("--set-hold-to-repeat",  type=str, help="define button hold mode")
  parser.add_argument("--set-usb-power-mode",  type=str, help="define auto wake and sleep")
  args = parser.parse_args()

  REVERSED_HID_KEYCODES = {v: k for k, v in HID_KEYCODES.items()}

  if args.set_key_btn and args.set_key_btn not in REVERSED_HID_KEYCODES:
    print("invalid key-btn value")
    sys.exit(1)
  if args.set_key_coin and args.set_key_coin not in REVERSED_HID_KEYCODES:
    print("invalid key-coin value")
    sys.exit(1)

  controller = CoinDeviceController()

  try:
    controller.connect()

    # read configuration
    config = controller.get_device_config()

    # setting a key
    if args.set_key_btn or args.set_key_coin or args.set_ssr_en or args.set_kbd_en or args.set_piggy_bank or args.set_auto_power_down or args.set_hold_to_repeat or args.set_usb_power_mode:
      # compute value to set. None in case this is already the value set
      set_key_btn_val  = REVERSED_HID_KEYCODES[args.set_key_btn]  if args.set_key_btn  and REVERSED_HID_KEYCODES[args.set_key_btn]  != config["keyBtn"]  else None
      set_key_coin_val = REVERSED_HID_KEYCODES[args.set_key_coin] if args.set_key_coin and REVERSED_HID_KEYCODES[args.set_key_coin] != config["keyCoin"] else None
      set_ssr_en          = str2bool(args.set_ssr_en)          if args.set_ssr_en          and str2bool(args.set_ssr_en)          != config["ssrEn"]         else None
      set_kbd_en          = str2bool(args.set_kbd_en)          if args.set_kbd_en          and str2bool(args.set_kbd_en)          != config["kbdEn"]         else None
      set_piggy_bank      = str2bool(args.set_piggy_bank)      if args.set_piggy_bank      and str2bool(args.set_piggy_bank)      != config["piggyBank"]     else None
      set_auto_power_down = str2bool(args.set_auto_power_down) if args.set_auto_power_down and str2bool(args.set_auto_power_down) != config["autoPowerDown"] else None
      set_hold_to_repeat  = str2bool(args.set_hold_to_repeat)  if args.set_hold_to_repeat  and str2bool(args.set_hold_to_repeat)  != config["holdToRepeat"]  else None
      set_usb_power_mode  = str2bool(args.set_usb_power_mode)  if args.set_usb_power_mode  and str2bool(args.set_usb_power_mode)  != config["usbPowerMode"]  else None

      # don't set in case there is nothing to do
      if(set_key_btn_val    is None and set_key_coin_val is None and set_ssr_en          is None and
         set_kbd_en         is None and set_piggy_bank   is None and set_auto_power_down is None and
         set_hold_to_repeat is None and set_usb_power_mode is None):
        print("Values are already set in configuration.")
      else:
        controller.send_config(
          config,
          keyBtn        = set_key_btn_val,
          keyCoin       = set_key_coin_val,
          ssrEn         = set_ssr_en,
          kbdEn         = set_kbd_en,
          piggyBank     = set_piggy_bank,
          autoPowerDown = set_auto_power_down,
          holdToRepeat  = set_hold_to_repeat,
          usbPowerMode  = set_usb_power_mode
        )
    else:
      controller.print_device_config(config)

  except IOError as ex:
    print(f"error : {ex}")
  finally:
    controller.close()

###
