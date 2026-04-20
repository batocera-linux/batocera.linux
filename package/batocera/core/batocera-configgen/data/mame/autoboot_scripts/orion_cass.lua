-- orion_cass.lua

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

-- --- Load butons ---
common_autoboot.populate_buttons(button)

-- --- Print Info ---
common_autoboot.print_image_info()
common_autoboot.print_buttons(button)

-- --- Cassette Loading Handler Setup ---
local CASSETTE_SLOT = 1
local CASSETTE_DEVICE_TAG = manager.machine.images:at(CASSETTE_SLOT).device.tag
local cassette_handler = common_autoboot.create_cassette_handler(CASSETTE_DEVICE_TAG) 


-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = 100 -- common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local function create_boot_default_sequence(frame_num, cassette_monitor_func) -- 'cassette_monitor_func' is the per-frame callable handler
    local sequence_state = 0
    -- Define states for clarity
    local STATES = {
        INIT_PRE_LOAD_ACTIONS = 0, -- Initial actions before CLOAD/PLAY
        PLAY_CASS_INITIATED = 1,   -- CLOAD/PLAY commands sent, waiting for motor to spin up
        LOADING_CASS = 2,          -- Cassette motor is ON, monitoring for completion
        CASS_LOAD_DONE = 3,        -- Cassette has finished loading, waiting for post-load actions
        POST_LOAD_ACTIONS = 4,     -- Executing actions after cassette load
        COMPLETE = 5               -- Sequence finished
    }
    
    local post_load_start_frame = 0 -- Frame at which post-load actions began

    return function(current_frame_num) -- This inner function runs every frame
        -- Always call cassette_monitor_func once we are in a state where loading should be active.
        -- This ensures continuous monitoring, throttling, and detection of load completion.
        if sequence_state >= STATES.LOADING_CASS and sequence_state < STATES.CASS_LOAD_DONE then
            local cassette_load_done = cassette_monitor_func(current_frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)
            if cassette_load_done then
                sequence_state = STATES.CASS_LOAD_DONE -- Transition directly to CASS_LOAD_DONE
                post_load_start_frame = current_frame_num -- Mark start for relative timing of post-actions
                emu.print_info("Boot Default: Cassette loading is complete (triggered by handler). Transitioning to post-load actions.")
                return -- Exit early for this frame after state change, to prevent double-execution
            end
        end

        -- --- State Machine Logic ---
        if sequence_state == STATES.INIT_PRE_LOAD_ACTIONS then
            -- Schedule initial pre-load actions
            common_autoboot.press_and_release(button, current_frame_num, "Cursor Down", 100, 1)
            common_autoboot.press_and_release(button, current_frame_num, "Cursor Down", 110, 1)
            common_autoboot.press_and_release(button, current_frame_num, "Cursor Down", 120, 1)
            common_autoboot.press_and_release(button, current_frame_num, "Enter", 150, BUTTON_PRESS_DURATION)
            common_autoboot.type_at_frame(current_frame_num, "A\n", 200)

            common_autoboot.play_cassette_at_frame(current_frame_num, CASSETTE_DEVICE_TAG, 350)
            
            -- Transition to PLAY_CASS_INITIATED after these actions are scheduled (at the last target frame or beyond)
            if current_frame_num >= 350 then
                sequence_state = STATES.PLAY_CASS_INITIATED
                emu.print_info("Boot Default: Pre-load actions scheduled. Waiting for cassette motor to engage.")
            end
            
        elseif sequence_state == STATES.PLAY_CASS_INITIATED then
            -- Wait for the cassette motor to actually spin up
            local cassette_device = manager.machine.cassettes[CASSETTE_DEVICE_TAG]
            if cassette_device and cassette_device.motor_state == true then
                sequence_state = STATES.LOADING_CASS
                emu.print_info("Boot Default: Cassette motor confirmed ON. Beginning continuous monitoring.")
            end

        -- If sequence_state becomes CASS_LOAD_DONE (from the monitor above), this block is skipped,
        -- and the logic will fall through to the next `elseif` for POST_LOAD_ACTIONS in the subsequent frame.

        elseif sequence_state == STATES.CASS_LOAD_DONE then
            -- This state is primarily a transition point.
            -- The 'RUN' command is NOT issued here. It's issued by the cassette_monitor_func internally.
            -- We transition immediately to POST_LOAD_ACTIONS after load is detected.
            sequence_state = STATES.POST_LOAD_ACTIONS
            emu.print_info("Boot Default: Transitioning to post-load actions.")

        elseif sequence_state == STATES.POST_LOAD_ACTIONS then
            -- --- Actions to perform AFTER cassette load is done ---
            -- Use `post_load_start_frame` for relative timing
            common_autoboot.press_and_release(button, current_frame_num, "F4", post_load_start_frame + 300, 1)
            common_autoboot.press_and_release(button, current_frame_num, "Cursor Right", post_load_start_frame + 400, 1)
            common_autoboot.press_and_release(button, current_frame_num, "Cursor Down", post_load_start_frame + 410, 1)
            common_autoboot.press_and_release(button, current_frame_num, "Enter", post_load_start_frame + 420, BUTTON_PRESS_DURATION)

            -- Check if all post-load actions are completed
            if current_frame_num >= post_load_start_frame + 1000 + BUTTON_PRESS_DURATION then
                sequence_state = STATES.COMPLETE
                emu.print_info("Boot Default: All post-load actions completed. Sequence finished.")
            end

        elseif sequence_state == STATES.COMPLETE then
            -- Do nothing, sequence is finished.
        end
    end
end

-- --- Main Script Logic ---

-- Determine the currently loaded software name
local current_software_name = manager.machine.images:at(CASSETTE_SLOT).filename

-- Map software names to their respective boot functions
local boot_sequences = {
    ['default'] = create_boot_default_sequence(frame_num, cassette_handler),
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
        boot_function(frame_num, cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)