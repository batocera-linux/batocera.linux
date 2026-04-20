-- pecom_cass.lua

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")

local frame_num = 0

-- Build button table keyed by "port_tag,mask,type" for direct key presses (juku.lua style)
local button = {}
for _, port in pairs(manager.machine.ioport.ports) do
    for _, field in pairs(port.fields) do
        button[field.port.tag .. "," .. field.mask .. "," .. field.type] = field
    end
end

common_autoboot.print_image_info()

local CASSETTE_DEVICE_TAG             = ":cassette"
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

-- RUN key IDs (port_tag, mask, IPT_KEYBOARD=49)
-- Source: src/mame/sfrj/pecom.cpp
local KEY = {
    R      = ":LINE19,1,49",
    U      = ":LINE20,2,49",
    N      = ":LINE17,1,49",
    RETURN = ":LINE0,1,49",
}
local KEY_DURATION = 5
local KEY_GAP      = 10

local function press_key(id, press_frame)
    if not button[id] then return end
    if frame_num == press_frame then
        button[id]:set_value(1)
    elseif frame_num == press_frame + KEY_DURATION then
        button[id]:set_value(0)
    end
end

-- is_stopped-based handler: works even when the Pecom does not assert motor_state.
-- Mirrors the approach used in mc10_cass.lua.
local function create_pecom_cassette_handler(tag)
    local stop_frame  = 0
    local seen_playing = false
    local load_done   = false

    return function(current_frame_num, delay)
        local dev = manager.machine.cassettes[tag]
        if not dev then
            emu.print_info("WARNING: Cassette device '" .. tag .. "' not found!")
            return false
        end

        if dev.is_stopped == false then
            manager.machine.video.throttled = false
            manager.machine.video.frameskip = 12
            seen_playing = true
        else
            manager.machine.video.throttled = true
            manager.machine.video.frameskip = 0
            if seen_playing and stop_frame == 0 then
                stop_frame = current_frame_num
                emu.print_info("[Pecom] Cassette stopped at frame " .. current_frame_num)
            end
        end

        if not load_done and stop_frame ~= 0 and current_frame_num > stop_frame + delay then
            load_done = true
            emu.print_info("[Pecom] Cassette load complete at frame " .. current_frame_num)
            return true
        end

        return false
    end
end

local cassette_handler = create_pecom_cassette_handler(CASSETTE_DEVICE_TAG)
local post_load_frame  = nil

local function boot_default()
    common_autoboot.type_at_frame(frame_num, "PLOAD\n", 50)
    common_autoboot.play_cassette_at_frame(frame_num, CASSETTE_DEVICE_TAG, 150)

    if cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES) then
        post_load_frame = frame_num
    end

    -- Type RUN + Return via direct key presses to avoid natural-keyboard case issues
    if post_load_frame then
        local base = post_load_frame + 10
        press_key(KEY.R,      base)
        press_key(KEY.U,      base + (KEY_DURATION + KEY_GAP))
        press_key(KEY.N,      base + (KEY_DURATION + KEY_GAP) * 2)
        press_key(KEY.RETURN, base + (KEY_DURATION + KEY_GAP) * 3)
    end
end

local current_software_name = manager.machine.images:at(1).filename

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        emu.print_info("Loaded Software: " .. current_software_name)
    end

    common_autoboot.debug_frame_num(frame_num)

    boot_default()
end

subscription = emu.add_machine_frame_notifier(process_frame)
