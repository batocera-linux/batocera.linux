-- dragon_cass.lua
--
-- Dragon cassette autoboot with CoCo/Dragon CAS header parsing.
-- This is a safer default than blind CLOAD/RUN:
--   type 0 (BASIC)   -> CLOAD, then RUN after load completes
--   type 2 (machine) -> CLOADM:EXEC when load >= $01A9, else CLOADM
--
-- RUN is sent via whichever fires first:
--   a) Hardware cassette motor turns off (works for CAS with EOF block + raw audio)
--   b) Dragon BASIC "OK" prompt detected on screen (fallback for CAS without EOF block)

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local CAS_SCAN_BYTES = 4096

local TAPE_TYPE_BASIC = 0
local TAPE_TYPE_DATA = 1
local TAPE_TYPE_MACHINE = 2

local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION
local CASSETTE_MOTOR_OFF_DELAY_FRAMES = common_autoboot.DEFAULT_CASSETTE_MOTOR_OFF_DELAY_FRAMES

-- Dragon video RAM: 0x0400-0x05FF, 32 cols x 16 rows
local DRAGON_SCREEN_RAM  = 0x0400
local DRAGON_SCREEN_COLS = 32
local DRAGON_SCREEN_ROWS = 16

local button = {}
local frame_num = 0

common_autoboot.populate_buttons(button)

local function be16(data, pos)
    local hi = data:byte(pos) or 0
    local lo = data:byte(pos + 1) or 0
    return (hi << 8) | lo
end

local function find_cassette_path()
    for _, cass in pairs(manager.machine.cassettes) do
        if cass.exists and cass.filename and #cass.filename > 0 then
            print("[Dragon Autoboot] Cassette device: " .. cass.filename)
            return cass.filename
        end
    end

    for _, img in pairs(manager.machine.images) do
        if img.exists and img.filename and #img.filename > 0 then
            local fn = img.filename:lower()
            if fn:find("%.cas$") or fn:find("%.wav$") then
                print("[Dragon Autoboot] Image device cassette: " .. img.filename)
                return img.filename
            end
        end
    end

    return nil
end

local function parse_cas_header(data)
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
                local file_type = data:byte(dstart + 8)
                local start_address = be16(data, dstart + 11)
                local load_address = be16(data, dstart + 13)
                local name = {}

                for fi = 0, 7 do
                    local c = data:byte(dstart + fi)
                    if c and c ~= 0x20 and c ~= 0x00 then
                        table.insert(name, string.char(c))
                    end
                end

                print(string.format(
                    "[Dragon Autoboot] CAS header: file='%s' type=%d load=0x%04X exec=0x%04X",
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
    print("[Dragon Autoboot] --- Tape type detection ---")

    local path = find_cassette_path()
    if not path then
        print("[Dragon Autoboot] No cassette image found.")
        return { file_type = TAPE_TYPE_BASIC, load_address = 0 }
    end

    local data = zip_util.read_bytes(path, CAS_SCAN_BYTES)
    if not data then
        print("[Dragon Autoboot] Could not read cassette data, defaulting to BASIC.")
        return { file_type = TAPE_TYPE_BASIC, load_address = 0 }
    end

    local info = parse_cas_header(data)
    if info then
        return info
    end

    print("[Dragon Autoboot] No valid CAS header found, defaulting to BASIC.")
    return { file_type = TAPE_TYPE_BASIC, load_address = 0 }
end

-- ── Low-level helpers ─────────────────────────────────────────────────────────

local function vram_read(addr)
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return nil end
    local mem = cpu.spaces["program"]
    if not mem then return nil end
    return mem:read_u8(addr)
end

-- Returns true if bytes b1,b2 look like Dragon BASIC's "OK" string.
-- Dragon MC6847 alphanumeric: 'A'=0x01…'Z'=0x1A (ASCII minus 0x40).
--   'O'=0x0F, 'K'=0x0B
-- Some Dragon 64 ROMs may write raw ASCII values instead:
--   'O'=0x4F, 'K'=0x4B
local function is_ok_bytes(b1, b2)
    return (b1 == 0x0F and b2 == 0x0B) or   -- MC6847 native
           (b1 == 0x4F and b2 == 0x4B)        -- raw ASCII
end

-- Scan entire video RAM; return a table of {addr=true} for every "OK" found.
local function collect_ok_addrs()
    local found = {}
    for row = 0, DRAGON_SCREEN_ROWS - 1 do
        for col = 0, DRAGON_SCREEN_COLS - 2 do
            local addr = DRAGON_SCREEN_RAM + row * DRAGON_SCREEN_COLS + col
            local b1 = vram_read(addr)
            local b2 = vram_read(addr + 1)
            if b1 and b2 and is_ok_bytes(b1, b2) then
                found[addr] = true
            end
        end
    end
    return found
end

-- Dump a single row of video RAM as hex for diagnostics.
local function dump_vram_row(row)
    local bytes = {}
    for col = 0, DRAGON_SCREEN_COLS - 1 do
        local b = vram_read(DRAGON_SCREEN_RAM + row * DRAGON_SCREEN_COLS + col)
        table.insert(bytes, b and string.format("%02X", b) or "??")
    end
    print(string.format("[Dragon Autoboot] VRAM row %2d: %s", row, table.concat(bytes, " ")))
end

-- ── Boot state ────────────────────────────────────────────────────────────────

local ok_baseline     = {}    -- OK addresses present before tape plays
local ok_baseline_done = false
local ok_seen_frame   = 0
local motor_was_on    = false
local motor_off_start = 0
local run_sent        = false
local cassette_handler = common_autoboot.create_cassette_handler(":cassette")
local tape_info       = nil

local function send_run()
    print("[Dragon Autoboot] Sending RUN at frame " .. frame_num)
    manager.machine.video.throttled = true
    manager.machine.video.frameskip = 0
    emu.keypost("RUN\n")
    run_sent = true
end

-- ── boot_basic ────────────────────────────────────────────────────────────────

local function boot_basic()
    common_autoboot.type_at_frame(frame_num, "CLOAD\n", 200, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 300)

    if run_sent then return end

    -- Hold throttle OFF from the moment the tape starts until completion.
    -- We manage this directly rather than relying on cassette_handler so that
    -- brief motor toggles between blocks don't stutter back to normal speed.
    if frame_num >= 300 then
        manager.machine.video.throttled = false
        manager.machine.video.frameskip = 12
    end

    -- ── Baseline capture ───────────────────────────────────────────────────
    -- Snapshot any "OK" already on screen (from the Dragon BASIC startup banner)
    -- just after CLOAD is typed but well before the tape data arrives.
    if frame_num == 350 then
        ok_baseline = collect_ok_addrs()
        ok_baseline_done = true
        local n = 0
        for _ in pairs(ok_baseline) do n = n + 1 end
        print(string.format("[Dragon Autoboot] Baseline: %d OK addr(s) in VRAM", n))
        -- Dump first 4 rows for diagnosis
        for r = 0, 3 do dump_vram_row(r) end
    end

    -- ── Periodic diagnostics ──────────────────────────────────────────────
    if frame_num % 600 == 0 and frame_num > 300 then
        local cass = manager.machine.cassettes[":cassette"]
        local ms   = cass and tostring(cass.motor_state)  or "n/a"
        local ist  = cass and tostring(cass.is_stopped)   or "n/a"
        local b0   = vram_read(DRAGON_SCREEN_RAM)
        print(string.format("[Dragon Autoboot] frame=%d motor=%s is_stopped=%s vram[0]=0x%s",
            frame_num, ms, ist, b0 and string.format("%02X", b0) or "??"))
    end

    -- ── Method 1: hardware motor turns off ────────────────────────────────
    -- Track when motor was on, then detect it going off with a short debounce.
    if frame_num > 360 then
        local cass = manager.machine.cassettes[":cassette"]
        local motor = cass and cass.motor_state or nil
        if motor == true then
            motor_was_on = true
            motor_off_start = 0
        elseif motor == false and motor_was_on then
            if motor_off_start == 0 then
                motor_off_start = frame_num
                print("[Dragon Autoboot] Motor OFF at frame " .. frame_num)
            elseif frame_num >= motor_off_start + CASSETTE_MOTOR_OFF_DELAY_FRAMES then
                print("[Dragon Autoboot] Motor off confirmed → RUN")
                send_run()
                return
            end
        end
    end

    -- ── Method 2: "OK" prompt on screen ───────────────────────────────────
    -- Dragon BASIC always prints "OK" when returning to the command prompt.
    -- Check every 30 frames to keep overhead low.
    if ok_baseline_done and frame_num >= 400 and frame_num % 30 == 0 then
        local new_ok = false
        local current = collect_ok_addrs()
        for addr in pairs(current) do
            if not ok_baseline[addr] then
                local row = math.floor((addr - DRAGON_SCREEN_RAM) / DRAGON_SCREEN_COLS)
                local col = (addr - DRAGON_SCREEN_RAM) % DRAGON_SCREEN_COLS
                local b1  = vram_read(addr)
                print(string.format("[Dragon Autoboot] New OK row=%d col=%d addr=0x%04X b1=0x%02X frame=%d",
                    row, col, addr, b1 or 0, frame_num))
                new_ok = true
                break
            end
        end

        if new_ok then
            if ok_seen_frame == 0 then
                ok_seen_frame = frame_num
                -- Dump last rows when we first see it, to verify encoding
                for r = 12, 15 do dump_vram_row(r) end
            elseif frame_num >= ok_seen_frame + 30 then
                print("[Dragon Autoboot] Screen OK confirmed → RUN")
                send_run()
            end
        else
            ok_seen_frame = 0
        end
    end
end

local function boot_machine()
    local need_exec = (tape_info.load_address or 0) >= 0x01A9
    local cmd = need_exec and "CLOADM:EXEC\n" or "CLOADM\n"

    common_autoboot.type_at_frame(frame_num, cmd, 200, BUTTON_PRESS_DURATION)
    common_autoboot.play_cassette_at_frame(frame_num, ":cassette", 300)

    cassette_handler(frame_num, CASSETTE_MOTOR_OFF_DELAY_FRAMES)
end

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        common_autoboot.print_image_info()
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
