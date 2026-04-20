-- mtx_cass.lua

-- Load common autoboot functions
local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

-- Script-wide variables
local button = {}
local frame_num = 0

-- --- Cassette Loading Handler Setup ---
local CASSETTE_SLOT = 4
local CASSETTE_DEVICE_TAG = manager.machine.images:at(CASSETTE_SLOT).device.tag
local cassette_handler = common_autoboot.create_cassette_handler(CASSETTE_DEVICE_TAG)

common_autoboot.populate_buttons(button)

common_autoboot.print_image_info()

-- --- Constants for this specific script ---
local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

-- Detect MTX500-only games by filename.
-- Returns "mtx500_run" if the game needs POKE+NEW+LOAD+RUN,
--         "mtx500"     if the game needs POKE+NEW+LOAD (no RUN),
--         "default"    otherwise.
local function detect_game_type(filename)
    local lower = string.lower(filename)
    if lower:find("mtx500") or lower:find("mtx 500") then
        -- filename convention: (poke 64122,0--new--load--run) or (poke 64122,0--new--load)
        if lower:find("load%-%-run") or lower:find("load%-run") then
            return "mtx500_run"
        else
            return "mtx500"
        end
    end
    return "default"
end

local function boot_default(cassette_handler)
    common_autoboot.type_at_frame(frame_num, "LOAD\"\"\n", 100)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 200)

    local cassette_load_done = cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if cassette_load_done then
        -- emu.keypost('RUN\n')
    end
end

-- MTX500-only games: ROM at 0xFA00-0xFFFF must be banked out before loading.
-- POKE 64122,0 disables the MTX ROM overlay and maps RAM in its place.

-- Persistent state for motor detection and RUN scheduling
local mtx500_motor_was_on = false
local mtx500_motor_off_frame = 0
local mtx500_run_sent = false
local RUN_DELAY_FRAMES = 120

local function boot_mtx500_base(cassette_handler, with_run)
    common_autoboot.type_at_frame(frame_num, "POKE 64122,0\n", 100)
    common_autoboot.type_at_frame(frame_num, "NEW\n", 200)
    common_autoboot.type_at_frame(frame_num, "LOAD\"\"\n", 300)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 400)

    -- Use cassette_handler for throttle management only
    cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)

    if frame_num < 400 then return end

    -- Direct cassette state monitoring (independent of cassette_handler)
    local cass = manager.machine.cassettes[CASSETTE_DEVICE_TAG]
    if not cass then return end

    local playing = (cass.is_stopped == false) and (cass.motor_state == true)

    if playing then
        mtx500_motor_was_on = true
        mtx500_motor_off_frame = 0  -- reset if motor comes back on (inter-block gap)
    elseif mtx500_motor_was_on and mtx500_motor_off_frame == 0 then
        mtx500_motor_off_frame = frame_num
    end

    if with_run and not mtx500_run_sent
       and mtx500_motor_off_frame > 0
       and frame_num >= mtx500_motor_off_frame + RUN_DELAY_FRAMES then
        manager.machine.video.throttled = true
        manager.machine.video.frameskip = 0
        emu.keypost("RUN\n")
        mtx500_run_sent = true
    end
end

local function boot_mtx500(cassette_handler)
    boot_mtx500_base(cassette_handler, false)
end

local function boot_mtx500_run(cassette_handler)
    boot_mtx500_base(cassette_handler, true)
end

-- --- Main Script Logic ---

local current_software_name = manager.machine.images:at(CASSETTE_SLOT).filename
local game_type = detect_game_type(current_software_name)

local boot_sequences = {
    ['default']     = boot_default,
    ['mtx500']      = boot_mtx500,
    ['mtx500_run']  = boot_mtx500_run,
}

-- MAME machine frame notification callback
local function process_frame()
    frame_num = frame_num + 1

    -- Initial setup/info display at frame 1
    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        emu.print_info("Loaded Software Name (from image filename): " .. current_software_name)
        emu.print_info("--- Detected game type: " .. game_type .. " ---")
    end

    --- DEBUG: Print current frame number every 100 frames ---
    common_autoboot.debug_frame_num(frame_num)

    local boot_function = boot_sequences[game_type] or boot_sequences["default"]

    if boot_function then
        boot_function(cassette_handler)
    end
end

-- Subscribe to machine frame notifications
subscription = emu.add_machine_frame_notifier(process_frame)
