-- autoboot_zip.lua
-- Shared ZIP and file-reading utilities for MAME autoboot scripts.
--
-- Usage:
--   local zip_util = dofile("/usr/share/batocera/configgen/data/mame/autoboot_scripts/autoboot_zip.lua")
--   local data = zip_util.read_bytes(mame_filename, 4096)
--   local entry = zip_util.find_zip_entry(zippath, function(n) return n:lower():match("%.dsk$") end)

local function u16le(s, pos)
    return s:byte(pos) | (s:byte(pos+1) << 8)
end

local function u32le(s, pos)
    return s:byte(pos) | (s:byte(pos+1) << 8) | (s:byte(pos+2) << 16) | (s:byte(pos+3) << 24)
end

-- Parse a MAME image path into (kind, zippath, entrypath).
-- Virtual zip path:  /roms/game.zip/game.cas  →  "zip", "/roms/game.zip", "game.cas"
-- Plain file path:   /roms/game.cas            →  "plain", nil, "/roms/game.cas"
local function parse_mame_path(fullpath)
    local p = fullpath:gsub("\\", "/")
    local zippath, entry = p:match("^(.*%.zip)/(.+)$")
    if zippath and entry then return "zip", zippath, entry end
    return "plain", nil, p
end

-- Walk a ZIP file's local file headers and return the first entry name
-- for which match_fn(entryname) returns true, or nil.
local function find_zip_entry(zippath, match_fn)
    local f = io.open(zippath, "rb")
    if not f then return nil end
    local zipdata = f:read("*a")
    f:close()
    if not zipdata or #zipdata < 30 then return nil end

    local pos = 1
    while pos <= #zipdata - 30 do
        if zipdata:byte(pos)   ~= 0x50 or zipdata:byte(pos+1) ~= 0x4B or
           zipdata:byte(pos+2) ~= 0x03 or zipdata:byte(pos+3) ~= 0x04 then break end
        local comp_size  = u32le(zipdata, pos+18)
        local fname_len  = u16le(zipdata, pos+26)
        local extra_len  = u16le(zipdata, pos+28)
        local ename      = zipdata:sub(pos+30, pos+30+fname_len-1)
        local data_start = pos + 30 + fname_len + extra_len
        if match_fn(ename) then return ename end
        pos = data_start + comp_size
    end
    return nil
end

-- Read bytes of a named entry from a ZIP archive.
-- method=0 (stored)  : pure Lua, no external process.
-- method=8 (deflated): Python3 fallback.
-- max_bytes: maximum bytes to read, or nil to read the whole entry.
-- Returns a Lua byte-string, or nil on failure.
local function read_entry_from_zip(zippath, entryname, max_bytes)
    local f = io.open(zippath, "rb")
    if not f then return nil end
    local zipdata = f:read("*a")
    f:close()
    if not zipdata or #zipdata < 30 then return nil end

    local pos = 1
    while pos <= #zipdata - 30 do
        if zipdata:byte(pos)   ~= 0x50 or zipdata:byte(pos+1) ~= 0x4B or
           zipdata:byte(pos+2) ~= 0x03 or zipdata:byte(pos+3) ~= 0x04 then break end
        local method      = u16le(zipdata, pos+8)
        local comp_size   = u32le(zipdata, pos+18)
        local uncomp_size = u32le(zipdata, pos+22)
        local fname_len   = u16le(zipdata, pos+26)
        local extra_len   = u16le(zipdata, pos+28)
        local entry_name  = zipdata:sub(pos+30, pos+30+fname_len-1)
        local data_start  = pos + 30 + fname_len + extra_len

        if entry_name:lower() == entryname:lower() then
            if method == 0 then
                local nbytes = max_bytes and math.min(uncomp_size, max_bytes) or uncomp_size
                return zipdata:sub(data_start, data_start + nbytes - 1)
            elseif method == 8 then
                local zq   = zippath:gsub("'", "'\\''")
                local nq   = entryname:gsub("'", "'\\''")
                local pipe = io.popen(string.format(
                    "python3 -c 'import zipfile,sys; zf=zipfile.ZipFile(sys.argv[1]); sys.stdout.buffer.write(zf.read(sys.argv[2]))' '%s' '%s' 2>/dev/null",
                    zq, nq), "r")
                if not pipe then return nil end
                local raw = max_bytes and pipe:read(max_bytes) or pipe:read("*a")
                pipe:close()
                return (raw and #raw > 0) and raw or nil
            end
            return nil
        end

        pos = data_start + comp_size
    end
    return nil
end

-- Read bytes from a file, handling both plain files and MAME virtual zip paths.
-- max_bytes: maximum bytes to read, or nil to read everything.
-- Returns a Lua byte-string, or nil on failure.
local function read_bytes(mame_filename, max_bytes)
    local kind, zippath, entrypath = parse_mame_path(mame_filename)
    if kind == "zip" then
        return read_entry_from_zip(zippath, entrypath, max_bytes)
    end
    local f = io.open(entrypath, "rb")
    if not f then return nil end
    local data = max_bytes and f:read(max_bytes) or f:read("*a")
    f:close()
    return data
end

return {
    u16le               = u16le,
    u32le               = u32le,
    parse_mame_path     = parse_mame_path,
    find_zip_entry      = find_zip_entry,
    read_entry_from_zip = read_entry_from_zip,
    read_bytes          = read_bytes,
}
