-- einstein.lua
-- Most titles require DIR then run the .COM. Some titles are automatically run, esp. those that boot using XTALDOS 2.0
-- WIP: need to go through each games and see the .COM file

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

-- --- Map all buttons ---
common_autoboot.populate_buttons(button)

-- --- Print Info ---
common_autoboot.print_image_info()
-- common_autoboot.print_buttons(button)

local FLOPPY_SLOT = 2

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function boot_default(title_to_type)
    return function() 
        common_autoboot.type_at_frame(frame_num, title_to_type .. "\n", 300)
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(FLOPPY_SLOT).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    alice = boot_default("ALICE.COM"),
    chuckie = boot_default("CHUCKIE.COM"),
    pakman = boot_default("PAKMAN.COM"),
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