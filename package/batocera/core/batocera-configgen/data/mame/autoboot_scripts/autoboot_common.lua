-- autoboot_common.lua

-- Define common helper functions that will be used by other scripts.
-- These functions assume 'button' and 'frame_num' are available in the calling scope,
-- or they will need to be passed as arguments, which makes them truly independent.
-- For MAME Lua scripts, it's common to expect 'button' and 'frame_num' to be managed
-- by the main calling script.

-- --- Common Constants ---
local DEFAULT_BUTTON_PRESS_DURATION = 100 -- Default duration for button presses in frames
local DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES = 60 -- Default duration to wait after cassette stopped (after throttle)

-- Helper function to press and release a button at specific frame numbers
-- Assumes 'frame_num' is globally accessible (or passed in) and 'button' table is global
local function press_and_release_button(button_table, current_frame_num, button_name, press_frame, duration)
    local release_frame = press_frame + duration
    -- emu.print_info(string.format("Common: %s (Current Frame: %d, Target Press: %d, Target Release: %d)",
    --                              button_name, current_frame_num, press_frame, release_frame))

    if current_frame_num == press_frame then
        emu.print_info("!!!! PRESSING button: " .. button_name .. " at frame " .. current_frame_num .. " (Duration: " .. duration .. " frames) !!!!")
        if button_table[button_name] then
            button_table[button_name]:set_value(1)
        else
            emu.print_info("Warning: Button '" .. button_name .. "' not found for press.")
        end
    elseif current_frame_num == release_frame then
        emu.print_info("!!!! RELEASING button: " .. button_name .. " at frame " .. current_frame_num .. " !!!!")
        if button_table[button_name] then
            button_table[button_name]:set_value(0)
        else
            emu.print_info("Warning: Button '" .. button_name .. "' not found for release.")
        end
    end
end

-- Helper function to type a string at a specific frame number
-- Assumes 'frame_num' is globally accessible (or passed in)
local function type_string_at_frame(current_frame_num, text, start_frame)
    if current_frame_num == start_frame then
        emu.print_info("Typing: " .. text:gsub("\n", "\\n") .. " at frame " .. current_frame_num)
        emu.keypost(text)
    end
end

-- Function to populate the button table
-- It takes an empty table and populates it.
local function populate_button_table(target_button_table)
    for key, ports in pairs(manager.machine.ioport.ports) do
        for field_name, field in pairs(ports.fields) do
            target_button_table[field_name] = field
        end
    end
end

-- Function to get a list of device tag, e.g. :cassette. Some system uses :cassette1
-- local function print_device_tag()
--     emu.print_info("--- List of Device Tag ---")
--     print(manager.machine.images:at(3).device.tag)
--     emu.print_info("--- End of Device Tag ---")
-- end

local function print_image_info()
    emu.print_info("--- Loaded Image Information ---")
    local num_images = manager.machine.images:size()
    emu.print_info("Total loaded images: " .. num_images)

    if num_images == 0 then
        emu.print_info("No images currently loaded.")
    else
        -- Iterate through each image slot
        for i = 1, num_images do
            local image = manager.machine.images:at(i)
            if image then
                emu.print_info(string.format("  Image %d:", i))
                emu.print_info(string.format("    Device Tag: %s", image.device.tag or "N/A"))
                emu.print_info(string.format("    Filename: %s", image.filename or "N/A"))
                emu.print_info(string.format("    Mounted: %s", tostring(image.mounted)))
                emu.print_info(string.format("    Software Name: %s", image.software_name or "N/A")) -- From softlist, if applicable
                emu.print_info(string.format("    Is Cassette: %s", tostring(image.is_cassette)))
                emu.print_info(string.format("    Is Harddisk: %s", tostring(image.is_harddisk)))
                -- Add more properties as needed from the MAME Lua image_device documentation
            else
                emu.print_info(string.format("  Image %d: (Error: Could not retrieve image object)", i))
            end
        end
    end
    emu.print_info("--- End of Image Information ---")
end

-- Function to print the contents of the button table
local function print_button_table(button_table_to_print)
    emu.print_info("--- Contents of 'button' table ---")
    for field_name, field_object in pairs(button_table_to_print) do
        local current_value = field_object.value
        if current_value == nil then current_value = -1 end

        local type_class_name = field_object.type_class
        if type_class_name == nil then type_class_name = "unknown" end

        local info_string = string.format(
            "Key: '%s', Field Name: '%s', Current Value: %d, Type Class: %s",
            field_name,
            field_object.name,
            current_value,
            type_class_name
        )
        emu.print_info(info_string)
    end
    emu.print_info("--- End of 'button' table contents ---")
end

local function play_cassette_at_frame(current_frame_num, cassette_device_tag, start_frame)
    if current_frame_num == start_frame then
        local cassette_device = manager.machine.cassettes[cassette_device_tag]
        if cassette_device then
            cassette_device:play()
            emu.print_info("Playing cassette '" .. cassette_device_tag .. "' at frame " .. current_frame_num)
        else
            emu.print_info("WARNING: Cassette device '" .. cassette_device_tag .. "' not found for play at frame " .. current_frame_num)
        end
    end
end

-- New function for handling cassette throttling AND detecting load completion
-- This function now takes current_frame_num and returns true ONCE when loading is done.
-- It uses its own internal state variables, so they are not polluting the calling script.
local function create_cassette_handler(cassette_device_tag)
    local motor_state_false_frame_num = 0
    local load_done_flag = false -- This flag will be set to true ONCE when loading is complete
    local was_playing_and_throttling_off = false -- Tracks if we were actively loading and throttling was off

    return function(current_frame_num, delay_frames_after_motor_off)
        local cassette_device = manager.machine.cassettes[cassette_device_tag]
        if not cassette_device then
            emu.print_info("WARNING: Cassette device with tag '" .. cassette_device_tag .. "' not found!")
            return false
        end

        -- Handle throttling/frameskip
        if cassette_device.is_stopped == false and cassette_device.motor_state == true then
            manager.machine.video.throttled = false
            manager.machine.video.frameskip = 12
            was_playing_and_throttling_off = true -- Mark that it was actively playing (throttle disabled)
        else
            manager.machine.video.throttled = true
            manager.machine.video.frameskip = 0
            -- If it was just playing and throttling was off, and now it's stopped/motor off
            if was_playing_and_throttling_off and motor_state_false_frame_num == 0 then
                motor_state_false_frame_num = current_frame_num -- Mark the frame motor just turned off
                emu.print_info("Cassette motor OFF detected (and was loading) at frame " .. current_frame_num)
            end
            was_playing_and_throttling_off = false -- Reset, as it's no longer actively playing
        end


        -- Detect load completion AFTER the motor turns off and the delay passes
        if load_done_flag == false then -- Only process if load hasn't been marked done yet
            if motor_state_false_frame_num ~= 0 then -- Meaning the motor has turned off at some point
                -- This is the delay check:
                if current_frame_num > motor_state_false_frame_num + delay_frames_after_motor_off then
                    load_done_flag = true -- Mark loading as complete
                    emu.print_info("Cassette loading completed at frame " .. current_frame_num)
                    emu.print_info("Load done!!! (after delay)")
                    return true -- Signal that loading is done
                end
            end
        end

        return false -- Indicate loading is not yet done
    end
end

local function create_delay_logic()
    local delay_start_frame = 0
    local delay_in_frames = 0
    local delay_active = false

    -- This is the function that will be called continuously to check the delay state
    return function(current_frame_num, initiate_delay_frames)
        -- If initiate_delay_frames is provided, it means we want to START a new delay
        if initiate_delay_frames and not delay_active then
            delay_start_frame = current_frame_num
            delay_in_frames = initiate_delay_frames
            delay_active = true
            emu.print_info("Delay initiated at frame " .. current_frame_num .. " for " .. delay_in_frames .. " frames.")
            return false -- Delay just started, not done yet
        end

        -- If a delay is active, check if it's over
        if delay_active then
            if current_frame_num >= delay_start_frame + delay_in_frames then
                delay_active = false -- Delay is complete
                emu.print_info("Delay completed at frame " .. current_frame_num)
                return true -- Signal delay is over
            else
                return false -- Delay is still active
            end
        end

        return true -- No delay was active or initiated, so it's "done" by default.
    end
end

local function debug_frame_num(frame_num)
    if frame_num % 100 == 0 then -- The modulo operator (%) gives the remainder of a division
        emu.print_info("Current Frame: " .. frame_num)
    end
end    


-- Return a table of functions
return {
    press_and_release = press_and_release_button,
    type_at_frame = type_string_at_frame,
    populate_buttons = populate_button_table,
    print_buttons = print_button_table,      
    play_cassette_at_frame = play_cassette_at_frame, 
    create_cassette_handler = create_cassette_handler,
    create_delay_logic = create_delay_logic,
    DEFAULT_BUTTON_PRESS_DURATION = DEFAULT_BUTTON_PRESS_DURATION,
    DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES = DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES,
    print_image_info = print_image_info,
    print_device_tag = print_device_tag,
    debug_frame_num = debug_frame_num,
}