import os
import batoceraFiles
from os import path
import codecs
from utils.logger import get_logger

eslog = get_logger(__name__)

rpcs3_input_dir = batoceraFiles.CONF + "/rpcs3/input_configs/global"

def generateControllerConfig(system, controllers, rom):
    
    if not path.isdir(rpcs3_input_dir):
        os.makedirs(rpcs3_input_dir)
        
    valid_sony_guids = [
        # ds3
        "030000004c0500006802000011010000",
        "030000004c0500006802000011810000",
        "050000004c0500006802000000800000",
        "050000004c0500006802000000000000",
        # ds4
        "030000004c050000c405000011810000",
        "050000004c050000c405000000810000",
        "030000004c050000cc09000011010000",
        "050000004c050000cc09000000010000",
        "030000004c050000cc09000011810000",
        "050000004c050000cc09000000810000",
        "030000004c050000a00b000011010000",
        "030000004c050000a00b000011810000",
        # ds5
        "030000004c050000e60c000011810000",
        "050000004c050000e60c000000810000"
    ]
    
    # may need to expand this to support more controllers
    # from evdev_joystick_handler.h
    input_mapping = [
        ("up", "Up", [("BTN_DPAD_UP", "D-Pad Up"), ("ABS_HAT0Y", "Hat0 Y-")]),
        ("down", "Down", [("BTN_DPAD_DOWN", "D-Pad Down"), ("ABS_HAT0Y", "Hat0 Y+")]),
        ("left", "Left", [("BTN_DPAD_LEFT", "D-Pad Left"), ("ABS_HAT0X", "Hat0 X-")]),
        ("right", "Right", [("BTN_DPAD_RIGHT", "D-Pad Right"), ("ABS_HAT0X", "Hat0 X+")]),
        ("l2", "L2", [("BTN_TL2", "TL 2"), ("ABS_Z", "LZ+")]),
        ("r2", "R2", [("BTN_TR2", "TR 2"), ("ABS_RZ", "RZ+")]),
        ("a", "Cross", [("BTN_A", "A")]),
        ("b", "Circle", [("BTN_B", "B")]),
        ("x", "Square", [("BTN_X", "X")]),
        ("y", "Triangle", [("BTN_Y", "Y")]),
        ("joystick1up", "Left Stick Up", [("ABS_Y", "LY-")]),
        ("joystick1left", "Left Stick Left", [("ABS_X", "LX-")]),
        ("joystick2up", "Right Stick Up", [("ABS_RY", "RY-")]),
        ("joystick2left", "Right Stick Left", [("ABS_RX", "RX-")])
    ]
    
    mapping_dict = {}
    for input_name, config_name, event_variations in input_mapping:
        mapping_dict[input_name] = {
            "config_name": config_name,
            "event_variations": event_variations,
        }
    
    nplayer, ds3player, ds4player, dsplayer = 1, 1, 1, 1
    controller_counts = {}

    configFileName = f"{rpcs3_input_dir}/Default.yml"
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")
    for controller, pad in sorted(controllers.items()):
        if nplayer <= 7:
            eslog.debug(f"Controller #{nplayer} - {pad.guid}")
            # check for DualShock / DualSense
            if pad.guid in valid_sony_guids and f"rpcs3_controller{nplayer}" in system.config and system.config[f"rpcs3_controller{nplayer}"] == "Sony":
                eslog.debug("*** Using DualShock / DualSense configuration ***")
                # dualshock 3
                if pad.guid in valid_sony_guids[:4]:
                    f.write(f'Player {nplayer} Input:\n')
                    f.write('  Handler: DualShock 3\n')
                    f.write(f'  Device: "DS3 Pad #{ds3player}"\n')
                    ds3player += 1
                # dualshock 4
                elif pad.guid in valid_sony_guids[4:12]:
                    f.write(f'Player {nplayer} Input:\n')
                    f.write('  Handler: DualShock 4\n')
                    f.write(f'  Device: "DS4 Pad #{ds4player}"\n')
                    ds4player += 1
                # dualsense
                else:
                    f.write(f'Player {nplayer} Input:\n')
                    f.write('  Handler: DualSense\n')
                    f.write(f'  Device: "DualSense Pad #{dsplayer}"\n')
                    dsplayer += 1
                f.write('  Config:\n')
                f.write('    Left Stick Left: LS X-\n')
                f.write('    Left Stick Down: LS Y-\n')
                f.write('    Left Stick Right: LS X+\n')
                f.write('    Left Stick Up: LS Y+\n')
                f.write('    Right Stick Left: RS X-\n')
                f.write('    Right Stick Down: RS Y-\n')
                f.write('    Right Stick Right: RS X+\n')
                f.write('    Right Stick Up: RS Y+\n')
                f.write('    Start: Options\n')
                f.write('    Select: Share\n')
                f.write('    PS Button: PS Button\n')
                f.write('    Square: Square\n')
                f.write('    Cross: Cross\n')
                f.write('    Circle: Circle\n')
                f.write('    Triangle: Triangle\n')
                f.write('    Left: Left\n')
                f.write('    Down: Down\n')
                f.write('    Right: Right\n')
                f.write('    Up: Up\n')
                f.write('    R1: R1\n')
                f.write('    R2: R2\n')
                f.write('    R3: R3\n')
                f.write('    L1: L1\n')
                f.write('    L2: L2\n')
                f.write('    L3: L3\n')
                f.write('    Motion Sensor X:\n')
                f.write('      Axis: ""\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Motion Sensor Y:\n')
                f.write('      Axis: ""\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Motion Sensor Z:\n')
                f.write('      Axis: ""\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Motion Sensor G:\n')
                f.write('      Axis: ""\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Pressure Intensity Button: ""\n')
                f.write('    Pressure Intensity Percent: 50\n')
                f.write('    Pressure Intensity Toggle Mode: false\n')
                f.write('    Left Stick Multiplier: 100\n')
                f.write('    Right Stick Multiplier: 100\n')
                f.write('    Left Stick Deadzone: 40\n')
                f.write('    Right Stick Deadzone: 40\n')
                f.write('    Left Trigger Threshold: 0\n')
                f.write('    Right Trigger Threshold: 0\n')
                f.write('    Left Pad Squircling Factor: 8000\n')
                f.write('    Right Pad Squircling Factor: 8000\n')
                f.write('    Color Value R: 0\n')
                f.write('    Color Value G: 0\n')
                f.write('    Color Value B: 20\n')
                f.write('    Blink LED when battery is below 20%: true\n')
                f.write('    Use LED as a battery indicator: false\n')
                f.write('    LED battery indicator brightness: 10\n')
                f.write('    Player LED enabled: true\n')
                f.write('    Enable Large Vibration Motor: true\n')
                f.write('    Enable Small Vibration Motor: true\n')
                f.write('    Switch Vibration Motors: false\n')
                f.write('    Mouse Movement Mode: Relative\n')
                f.write('    Mouse Deadzone X Axis: 60\n')
                f.write('    Mouse Deadzone Y Axis: 60\n')
                f.write('    Mouse Acceleration X Axis: 200\n')
                f.write('    Mouse Acceleration Y Axis: 250\n')
                f.write('    Left Stick Lerp Factor: 100\n')
                f.write('    Right Stick Lerp Factor: 100\n')
                f.write('    Analog Button Lerp Factor: 100\n')
                f.write('    Trigger Lerp Factor: 100\n')
                f.write('    Device Class Type: 0\n')
                f.write('    Vendor ID: 1356\n')
                f.write('    Product ID: 616\n')
                f.write('  Buddy Device: ""\n')
            elif f"rpcs3_controller{nplayer}" in system.config and system.config[f"rpcs3_controller{nplayer}"] == "Evdev":
                eslog.debug("*** Using EVDEV configuration ***")
                # evdev
                f.write(f'Player {nplayer} Input:\n')
                f.write('  Handler: Evdev\n')
                f.write(f'  Device: {pad.dev}\n')
                f.write('  Config:\n')
                f.write('    Start: Start\n')
                f.write('    Select: Select\n')
                f.write('    PS Button: Mode\n')
                for inputIdx in pad.inputs:
                    input = pad.inputs[inputIdx]
                    if input.name in mapping_dict:
                        config_name = mapping_dict[input.name]["config_name"]
                        event_variations = mapping_dict[input.name]["event_variations"]
                        for event_type, value_name in event_variations:
                            if "BTN" in event_type and input.type == "button":
                                f.write(f"    {config_name}: {value_name}\n")
                            elif "HAT" in event_type and input.type == "hat":
                                f.write(f"    {config_name}: {value_name}\n")
                            elif "ABS" in event_type and input.type == "axis":
                                # handle axis for sticks
                                if config_name == "Left Stick Up":
                                    f.write(f"    {config_name}: {value_name}\n")
                                    # write the down values also
                                    f.write(f"    Left Stick Down: LY+\n")
                                elif config_name == "Left Stick Left":
                                    f.write(f"    {config_name}: {value_name}\n")
                                    # write the right values also
                                    f.write(f"    Left Stick Right: LX+\n")
                                # here's the complicated bit, DirectInput uses z axis
                                elif config_name == "Right Stick Up":
                                    f.write(f"    {config_name}: {value_name}\n")
                                    # write the down values
                                    f.write(f"    Right Stick Down: RY+\n")
                                elif config_name == "Right Stick Left":
                                    f.write(f"    {config_name}: {value_name}\n")
                                    # write the right values
                                    f.write(f"    Right Stick Right: RX+\n")
                                else:
                                    f.write(f"    {config_name}: {value_name}\n")
                # continue with default settings
                f.write('    R1: TR\n')
                f.write('    R3: Thumb R\n')
                f.write('    L1: TL\n')
                f.write('    L3: Thumb L\n')
                f.write('    Motion Sensor X:\n')
                f.write('      Axis: X\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Motion Sensor Y:\n')
                f.write('      Axis: Y\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Motion Sensor Z:\n')
                f.write('      Axis: Z\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Motion Sensor G:\n')
                f.write('      Axis: RY\n')
                f.write('      Mirrored: false\n')
                f.write('      Shift: 0\n')
                f.write('    Pressure Intensity Button: ""\n')
                f.write('    Pressure Intensity Percent: 50\n')
                f.write('    Pressure Intensity Toggle Mode: false\n')
                f.write('    Left Stick Multiplier: 100\n')
                f.write('    Right Stick Multiplier: 100\n')
                f.write('    Left Stick Deadzone: 30\n')
                f.write('    Right Stick Deadzone: 30\n')
                f.write('    Left Trigger Threshold: 0\n')
                f.write('    Right Trigger Threshold: 0\n')
                f.write('    Left Pad Squircling Factor: 5000\n')
                f.write('    Right Pad Squircling Factor: 5000\n')
                f.write('    Color Value R: 0\n')
                f.write('    Color Value G: 0\n')
                f.write('    Color Value B: 0\n')
                f.write('    Blink LED when battery is below 20%: true\n')
                f.write('    Use LED as a battery indicator: false\n')
                f.write('    LED battery indicator brightness: 50\n')
                f.write('    Player LED enabled: true\n')
                f.write('    Enable Large Vibration Motor: true\n')
                f.write('    Enable Small Vibration Motor: true\n')
                f.write('    Switch Vibration Motors: false\n')
                f.write('    Mouse Movement Mode: Relative\n')
                f.write('    Mouse Deadzone X Axis: 60\n')
                f.write('    Mouse Deadzone Y Axis: 60\n')
                f.write('    Mouse Acceleration X Axis: 200\n')
                f.write('    Mouse Acceleration Y Axis: 250\n')
                f.write('    Left Stick Lerp Factor: 100\n')
                f.write('    Right Stick Lerp Factor: 100\n')
                f.write('    Analog Button Lerp Factor: 100\n')
                f.write('    Trigger Lerp Factor: 100\n')
                f.write('    Device Class Type: 0\n')
                f.write('    Vendor ID: 1356\n')
                f.write('    Product ID: 616\n')
                f.write('  Buddy Device: ""\n')
            else:
                eslog.debug("*** Using default SDL2 configuration ***")
                f.write(f'Player {nplayer} Input:\n')
                f.write(f'  Handler: SDL\n')
                # workaround controllers with commas in their name - like Nintendo
                ctrlname = pad.realName.split(',')[0].strip()
                # rpcs3 appends a unique number per controller name
                if ctrlname in controller_counts:
                    controller_counts[ctrlname] += 1
                else:
                    controller_counts[ctrlname] = 1
                f.write(f'  Device: {ctrlname} {controller_counts[ctrlname]}\n')
                f.write(f'  Config:\n')
                f.write(f'    Left Stick Left: LS X-\n')
                f.write(f'    Left Stick Down: LS Y-\n')
                f.write(f'    Left Stick Right: LS X+\n')
                f.write(f'    Left Stick Up: LS Y+\n')
                f.write(f'    Right Stick Left: RS X-\n')
                f.write(f'    Right Stick Down: RS Y-\n')
                f.write(f'    Right Stick Right: RS X+\n')
                f.write(f'    Right Stick Up: RS Y+\n')
                f.write(f'    Start: Start\n')
                f.write(f'    Select: Back\n')
                f.write(f'    PS Button: Guide\n')
                f.write(f'    Square: X\n')
                f.write(f'    Cross: A\n')
                f.write(f'    Circle: B\n')
                f.write(f'    Triangle: Y\n')
                f.write(f'    Left: Left\n')
                f.write(f'    Down: Down\n')
                f.write(f'    Right: Right\n')
                f.write(f'    Up: Up\n')
                f.write(f'    R1: RB\n')
                f.write(f'    R2: RT\n')
                f.write(f'    R3: RS\n')
                f.write(f'    L1: LB\n')
                f.write(f'    L2: LT\n')
                f.write(f'    L3: LS\n')
                f.write(f'    IR Nose: ""\n')
                f.write(f'    IR Tail: ""\n')
                f.write(f'    IR Left: ""\n')
                f.write(f'    IR Right: ""\n')
                f.write(f'    Tilt Left: ""\n')
                f.write(f'    Tilt Right: ""\n')
                f.write(f'    Motion Sensor X:\n')
                f.write(f'      Axis: X\n')
                f.write(f'      Mirrored: false\n')
                f.write(f'      Shift: 0\n')
                f.write(f'    Motion Sensor Y:\n')
                f.write(f'      Axis: Y\n')
                f.write(f'      Mirrored: false\n')
                f.write(f'      Shift: 0\n')
                f.write(f'    Motion Sensor Z:\n')
                f.write(f'      Axis: Z\n')
                f.write(f'      Mirrored: false\n')
                f.write(f'      Shift: 0\n')
                f.write(f'    Motion Sensor G:\n')
                f.write(f'      Axis: RY\n')
                f.write(f'      Mirrored: false\n')
                f.write(f'      Shift: 0\n')
                f.write(f'    Pressure Intensity Button: ""\n')
                f.write(f'    Pressure Intensity Percent: 50\n')
                f.write(f'    Pressure Intensity Toggle Mode: false\n')
                f.write(f'    Pressure Intensity Deadzone: 0\n')
                f.write(f'    Left Stick Multiplier: 100\n')
                f.write(f'    Right Stick Multiplier: 100\n')
                f.write(f'    Left Stick Deadzone: 8000\n')
                f.write(f'    Right Stick Deadzone: 8000\n')
                f.write(f'    Left Trigger Threshold: 0\n')
                f.write(f'    Right Trigger Threshold: 0\n')
                f.write(f'    Left Pad Squircling Factor: 8000\n')
                f.write(f'    Right Pad Squircling Factor: 8000\n')
                f.write(f'    Color Value R: 0\n')
                f.write(f'    Color Value G: 0\n')
                f.write(f'    Color Value B: 20\n')
                f.write(f'    Blink LED when battery is below 20%: true\n')
                f.write(f'    Use LED as a battery indicator: false\n')
                f.write(f'    LED battery indicator brightness: 10\n')
                f.write(f'    Player LED enabled: true\n')
                f.write(f'    Enable Large Vibration Motor: true\n')
                f.write(f'    Enable Small Vibration Motor: true\n')
                f.write(f'    Switch Vibration Motors: false\n')
                f.write(f'    Mouse Movement Mode: Relative\n')
                f.write(f'    Mouse Deadzone X Axis: 60\n')
                f.write(f'    Mouse Deadzone Y Axis: 60\n')
                f.write(f'    Mouse Acceleration X Axis: 200\n')
                f.write(f'    Mouse Acceleration Y Axis: 250\n')
                f.write(f'    Left Stick Lerp Factor: 100\n')
                f.write(f'    Right Stick Lerp Factor: 100\n')
                f.write(f'    Analog Button Lerp Factor: 100\n')
                f.write(f'    Trigger Lerp Factor: 100\n')
                f.write(f'    Device Class Type: 0\n')
                f.write(f'    Vendor ID: 1356\n')
                f.write(f'    Product ID: 616\n')
                f.write(f'  Buddy Device: ""\n')
        nplayer += 1
    f.close()
