-- tvc_flop.lua
--
-- TVC floppy autoboot (HBF expansion).
--
-- From MAME softlist notes:
--   Most titles can be run in BASIC with  LOAD"*"
--   If the program does not start automatically, follow with  RUN
--
-- Boot sequence:
--   1. Clear any initial prompt / splash (Enter at frame 300)
--   2. Type  LOAD"*"  to load the first program from the floppy
--   3. Wait a fixed delay for the disk to finish loading
--   4. Type  RUN  to start the program

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

local button    = {}
local frame_num = 0

common_autoboot.populate_buttons(button)
common_autoboot.print_image_info()

local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION

-- With the HBF expansion active the image order is:
--   1: printout  2: cartridge  3: floppydisk1  4: floppydisk2  5: cassette  6: quickload
local FLOP_SLOT = 3

-- Frames to wait after issuing LOAD"*" before sending RUN.
-- TVC floppy loads at ~300 RPM; a typical game takes up to ~20 s.
-- 1200 frames @ 50 fps = 24 s, which covers the vast majority of titles.
local FLOPPY_LOAD_DELAY_FRAMES = 1200

local LOAD_START_FRAME = 400
local RUN_FRAME        = LOAD_START_FRAME + FLOPPY_LOAD_DELAY_FRAMES

local current_software_name = manager.machine.images:at(FLOP_SLOT).filename

local function boot_default()
    common_autoboot.type_at_frame(frame_num, "\n",          300, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, 'LOAD"*"\n',   LOAD_START_FRAME, BUTTON_PRESS_DURATION)
    common_autoboot.type_at_frame(frame_num, "RUN\n",       RUN_FRAME,  BUTTON_PRESS_DURATION)
end

local boot_sequences = {
    ['default'] = boot_default,
}

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        emu.print_info("Loaded Software Name: " .. current_software_name)

        if boot_sequences[current_software_name] then
            emu.print_info("--- Booting using game-specific profile: " .. current_software_name .. " ---")
        else
            emu.print_info("--- Booting using default profile ---")
        end
    end

    common_autoboot.debug_frame_num(frame_num)

    local boot_function = boot_sequences[current_software_name] or boot_sequences["default"]
    if boot_function then
        boot_function()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
