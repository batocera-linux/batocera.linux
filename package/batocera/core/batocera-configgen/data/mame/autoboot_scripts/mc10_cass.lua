-- mc10_cass.lua
--
-- Dedicated MC-10 cassette autoboot.  This follows XRoar's basic autorun
-- heuristic more closely than trs80_cass.lua:
--   type 0 (BASIC)   -> CLOAD, then RUN after tape stops
--   type 2 (machine) -> CLOADM:EXEC only when load >= $01A9, else CLOADM
--
-- MC-10 tapes don't have the same remote motor-control behaviour as CoCo/TRS-80
-- setups, so load completion is tracked from cassette play/stop state rather
-- than motor_state.

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local CAS_SCAN_BYTES = 4096

local TAPE_TYPE_BASIC = 0
local TAPE_TYPE_DATA = 1
local TAPE_TYPE_MACHINE = 2

local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_STOP_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

local button = {}
local frame_num = 0

common_autoboot.populate_buttons(button)

local function be16(data, pos)
    local hi = data:byte(pos) or 0
    local lo = data:byte(pos + 1) or 0
    return (hi << 8) | lo
end

local function find_cassette_image()
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            return cass.filename, cass.device and cass.device.tag or ":cassette"
        end
    end

    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.cas$") or fn:find("%.c10$") then
                return img.filename, img.device and img.device.tag or ":cassette"
            end
        end
    end

    return nil, ":cassette"
end

local function parse_tape_header(data)
    if not data or #data < 20 then
        return nil
    end

    local i = 1
    local saw_leader = false

    while i <= #data do
        local b = data:byte(i)

        if b == 0x55 then
            saw_leader = true
            i = i + 1
        elseif b == 0x3C and saw_leader then
            local base = i + 1
            if base + 16 > #data then
                return nil
            end

            local block_type = data:byte(base)
            local block_size = data:byte(base + 1)

            if block_type == 0x00 and block_size >= 15 then
                local dstart = base + 2
                local name = {}
                for j = 0, 7 do
                    local c = data:byte(dstart + j)
                    if c and c ~= 0x00 and c ~= 0x20 then
                        table.insert(name, string.char(c))
                    end
                end

                local file_type = data:byte(dstart + 8)
                local start_address = be16(data, dstart + 11)
                local load_address = be16(data, dstart + 13)

                print(string.format(
                    "[MC-10 Autoboot] Header name='%s' type=%d load=0x%04X exec=0x%04X",
                    table.concat(name), file_type or -1, load_address, start_address))

                return {
                    file_type = file_type,
                    load_address = load_address,
                    start_address = start_address,
                }
            end

            saw_leader = false
            i = i + 1
        else
            saw_leader = false
            i = i + 1
        end
    end

    return nil
end

local function detect_tape_info()
    local path = find_cassette_image()
    if not path then
        print("[MC-10 Autoboot] No cassette image found.")
        return { file_type = TAPE_TYPE_BASIC, load_address = 0 }
    end

    print("[MC-10 Autoboot] Tape path: " .. path)
    local data = zip_util.read_bytes(path, CAS_SCAN_BYTES)
    if not data then
        print("[MC-10 Autoboot] Could not read tape header, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, load_address = 0 }
    end

    local info = parse_tape_header(data)
    if info then
        return info
    end

    print("[MC-10 Autoboot] No valid header found, defaulting to BASIC.")
    return { file_type = TAPE_TYPE_BASIC, load_address = 0 }
end

local function create_mc10_cassette_handler(cassette_device_tag)
    local stop_frame = 0
    local seen_playing = false
    local load_done = false

    return function(current_frame_num, delay_frames_after_stop)
        local cassette_device = manager.machine.cassettes[cassette_device_tag]
        if not cassette_device then
            print("[MC-10 Autoboot] Cassette device not found: " .. cassette_device_tag)
            return false
        end

        if cassette_device.is_stopped == false then
            manager.machine.video.throttled = false
            manager.machine.video.frameskip = 12
            seen_playing = true
        else
            manager.machine.video.throttled = true
            manager.machine.video.frameskip = 0
            if seen_playing and stop_frame == 0 then
                stop_frame = current_frame_num
                print("[MC-10 Autoboot] Cassette stop detected at frame " .. current_frame_num)
            end
        end

        if not load_done and stop_frame ~= 0 and current_frame_num > stop_frame + delay_frames_after_stop then
            load_done = true
            print("[MC-10 Autoboot] Cassette load complete at frame " .. current_frame_num)
            return true
        end

        return false
    end
end

local function play_cassette(cassette_tag, start_frame)
    if frame_num == start_frame then
        local cassette_device = manager.machine.cassettes[cassette_tag]
        if cassette_device then
            cassette_device:play()
            print("[MC-10 Autoboot] Playing cassette at frame " .. frame_num)
        else
            print("[MC-10 Autoboot] Cassette device not found for play: " .. cassette_tag)
        end
    end
end

local tape_info = nil
local cassette_tag = ":cassette"
local cassette_handler = nil

local function boot_basic()
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 140, BUTTON_PRESS_DURATION)
    play_cassette(cassette_tag, 260)

    if cassette_handler and cassette_handler(frame_num, CASSETTE_STOP_DELAY_FRAMES) then
        emu.keypost("RUN\n")
    end
end

local function boot_machine()
    local need_exec = (tape_info.load_address or 0) >= 0x01A9
    local cmd = need_exec and "CLOADM:EXEC\n" or "CLOADM\n"

    common_autoboot.type_at_frame(frame_num, cmd, 140, BUTTON_PRESS_DURATION)
    play_cassette(cassette_tag, 260)

    if cassette_handler then
        cassette_handler(frame_num, CASSETTE_STOP_DELAY_FRAMES)
    end
end

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        common_autoboot.print_image_info()
        local _, detected_tag = find_cassette_image()
        cassette_tag = detected_tag or ":cassette"
        cassette_handler = create_mc10_cassette_handler(cassette_tag)
        tape_info = detect_tape_info()
    end

    common_autoboot.debug_frame_num(frame_num)

    if not tape_info or tape_info.file_type == TAPE_TYPE_DATA then
        boot_basic()
    elseif tape_info.file_type == TAPE_TYPE_MACHINE then
        boot_machine()
    else
        boot_basic()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
