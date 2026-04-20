-- adam_flop.lua
--
-- Coleco ADAM floppy (SmartFDD) autoboot.
--
-- Boot flow:
--   EOS (Electronic Operating System) loads the first program from the floppy.
--   Most game disks contain T-DOS 4.5 (a CP/M-compatible OS by Tony Morehen)
--   as that first program.  T-DOS then gives an  A>  command prompt.
--
-- T-DOS autorun:
--   T-DOS 4.5 looks for a file called PROFILE.SUB on drive A: at boot.
--   If PROFILE.SUB exists the game starts automatically (no script needed).
--   If it does not exist, the user sees  A>  and must type the executable name.
--   Some disks have a PROFILE.SUB with a non-functional command (e.g. the game
--   title text); in those cases we wait for T-DOS to settle and type the correct
--   CP/M executable name ourselves.
--
-- Executable detection:
--   Scan the raw .dsk image for the first CP/M directory entry with a .COM
--   extension (user 0, extent 0, printable ASCII name).  This works regardless
--   of whether the softlist name matches the executable name.
--   Falls back to an uppercase/truncated version of the softlist name if
--   no .COM entry is found in the first 64 KB of the image.
--
-- Image slot order for the adam machine:
--   1: cassette1  2: cassette2  3: floppydisk1  4: floppydisk2  5-8: cartridge1-4

local common_autoboot = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_common.lua")
local zip_util        = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")

local button    = {}
local frame_num = 0

common_autoboot.populate_buttons(button)
common_autoboot.print_image_info()

local BUTTON_PRESS_DURATION = common_autoboot.DEFAULT_BUTTON_PRESS_DURATION

local FLOP_SLOT = 3   -- floppydisk1 is the third image slot

-- T-DOS finishes booting in ~5-7 s on real hardware; MAME emulates at ~60 Hz.
-- 600 frames (~10 s) gives a safe margin for T-DOS to load + PROFILE.SUB to fail
-- before we send the executable name.
local TDOS_PROMPT_FRAME = 600

local DSK_SCAN_BYTES = 65536  -- 64 KB covers the directory on any ADAM disk layout

-- ── CP/M directory scanner ────────────────────────────────────────────────────
--
-- CP/M directory entries are 32 bytes:
--   byte  0   : user number (0x00 = active user 0, 0xE5 = deleted)
--   bytes 1-8 : filename (8 chars, space-padded, high bit = attribute flag)
--   bytes 9-11: extension (3 chars, space-padded, high bit = attribute flag)
--   byte  12  : extent low (0 for first extent)
-- Entries are always 32-byte aligned within 512-byte sectors, so scanning at
-- 32-byte increments from offset 0 catches every directory entry.

local function find_first_com_on_disk(data)
    if not data then return nil end
    local n = #data
    local all_coms = {}

    for i = 1, n - 31, 32 do
        local user = data:byte(i)
        if user == 0x00 and data:byte(i+12) == 0x00 then  -- active entry, first extent
            -- Validate filename (bytes i+1..i+8): printable ASCII, mask off attribute bit
            local chars = {}
            local valid = true
            for j = i+1, i+8 do
                local c = data:byte(j) & 0x7F
                if c == 0x20 then
                    break  -- space = padding, end of name
                elseif c < 0x21 or c > 0x7E then
                    valid = false; break
                else
                    table.insert(chars, string.char(c))
                end
            end
            if valid and #chars > 0 then
                -- Check extension (bytes i+9..i+11) is COM
                local e1 = data:byte(i+9)  & 0x7F
                local e2 = data:byte(i+10) & 0x7F
                local e3 = data:byte(i+11) & 0x7F
                if e1 == 0x43 and e2 == 0x4F and e3 == 0x4D then  -- 'C','O','M'
                    local fname = table.concat(chars)
                    -- deduplicate
                    local seen = false
                    for _, v in ipairs(all_coms) do if v == fname then seen = true; break end end
                    if not seen then
                        table.insert(all_coms, fname)
                    end
                end
            end
        end
    end

    if #all_coms == 0 then
        print("[adam_flop] No .COM file found in directory scan")
        return nil
    end

    -- Prefer a COM whose name does not end with a column-mode suffix (-80, -40, 80, 40, _80, _40).
    -- The Infocom Zork disks list the 80-column version first; the plain version
    -- (ZORK1, ZORKII, ZORK-III) runs on the standard 40-column ADAM display.
    for _, fname in ipairs(all_coms) do
        if not fname:match("[-_]?[48]0$") then
            print(string.format("[adam_flop] Chosen COM (no col-suffix): %s.COM  (all: %s)",
                fname, table.concat(all_coms, ", ")))
            return fname
        end
    end

    -- All entries have a column-mode suffix — just use the first one.
    print(string.format("[adam_flop] Chosen COM (first, all suffixed): %s.COM", all_coms[1]))
    return all_coms[1]
end

local function detect_exe_name(mame_filename, fallback_key)
    print("[adam_flop] --- Scanning disk for first .COM file ---")
    local data = zip_util.read_bytes(mame_filename, DSK_SCAN_BYTES)
    local com_name = find_first_com_on_disk(data)
    if com_name then
        return com_name
    end
    local fallback = fallback_key:sub(1, 8):upper()
    print("[adam_flop] Falling back to softlist-derived name: " .. fallback)
    return fallback
end

-- ── Startup ───────────────────────────────────────────────────────────────────

local current_software_name = manager.machine.images:at(FLOP_SLOT).filename

-- software_key: base filename without path or extension, lowercased (for boot_sequences lookup)
local software_key = current_software_name:match("([^/\\]+)$")
software_key = software_key:gsub("%.%w+$", ""):lower()

-- Detect the actual CP/M executable name by scanning the disk image directory.
local exe_name = detect_exe_name(current_software_name, software_key)

-- ── Boot functions ────────────────────────────────────────────────────────────

local function boot_default()
    common_autoboot.type_at_frame(frame_num, exe_name .. "\n", TDOS_PROMPT_FRAME, BUTTON_PRESS_DURATION)
end

-- Per-game overrides — add entries here when disk scanning gives the wrong
-- result (e.g. the game has multiple .COM files and the second one is correct,
-- or a multi-step boot sequence is needed).
local boot_sequences = {
    ['default'] = boot_default,
}

-- ── Main ──────────────────────────────────────────────────────────────────────

local function process_frame()
    frame_num = frame_num + 1

    if frame_num == 1 then
        emu.print_info("System Driver: " .. emu.romname())
        emu.print_info("Loaded Software Name: " .. current_software_name)
        emu.print_info("[adam_flop] Software key: " .. software_key .. "  T-DOS executable: " .. exe_name)

        if boot_sequences[software_key] then
            emu.print_info("--- Booting using game-specific profile: " .. software_key .. " ---")
        else
            emu.print_info("--- Booting using default profile (will type: " .. exe_name .. ") ---")
        end
    end

    common_autoboot.debug_frame_num(frame_num)

    local boot_function = boot_sequences[software_key] or boot_sequences['default']
    if boot_function then
        boot_function()
    end
end

subscription = emu.add_machine_frame_notifier(process_frame)
