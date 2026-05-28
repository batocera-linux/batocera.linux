-- _cass.lua

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

local CARTRIDGE_SLOT = 3
local current_software_name = manager.machine.images:at(CARTRIDGE_SLOT).filename

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION

-- Press F10, then R 
local function boot_default()
    common_autoboot.press_and_release(button, frame_num, "Reset", 200, 10)
    common_autoboot.type_at_frame(frame_num, "R", 300)
end

-- --- Main Script Logic ---

-- Map software names to their respective boot functions
boot_sequences = {
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
        boot_function()
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)