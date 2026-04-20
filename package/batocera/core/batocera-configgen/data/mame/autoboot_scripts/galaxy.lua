-- galaxy.lua

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

-- Print Info
common_autoboot.print_image_info()

-- --- Cassette Loading Handler Setup ---
local CASSETTE_SLOT = 2
local CASSETTE_DEVICE_TAG = manager.machine.images:at(CASSETTE_SLOT).device.tag
local cassette_handler = common_autoboot.create_cassette_handler(CASSETTE_DEVICE_TAG) 

common_autoboot.populate_buttons(button)

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function boot_default(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "OLD\n", 100)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 200)

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if cassette_load_done then
        emu.keypost('RUN\n')
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(CASSETTE_SLOT).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    ['default'] = boot_default,
}

-- MAME machine frame notification callback
local function process_frame()
    frame_num = frame_num + 1

    -- Initial setup/info display at frame 1
    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        emu.print_info("Loaded Software Name (from image filename): " .. current_software_name)

        -- Determine which profile will be used 
        if boot_sequences[current_software_name] then
            emu.print_info("--- Booting using game specific profile: " .. current_software_name .. " ---")
        else
            emu.print_info("--- Booting using default profile ---")
        end        
    end

    --- DEBUG: Print current frame number every 100 frames ---
    common_autoboot.debug_frame_num(frame_num)

    -- Execute the relevant boot sequence based on the loaded software
    local boot_function = boot_sequences[current_software_name]

    if not boot_function then -- If specific function not found
        boot_function = boot_sequences["default"] -- Assign the default function
    end

    if boot_function then
        boot_function(cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)