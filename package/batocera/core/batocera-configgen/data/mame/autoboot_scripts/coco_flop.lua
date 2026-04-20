cpu = manager.machine.devices[":maincpu"]
mem = cpu.spaces["program"]
base_addr = 0x0400
base_file_name_size = 9
ext_file_name_size = 3
next_file = 32
file_index = 0
dir_frame = 0
try_run = 0
type_buffer = {}
type_qty = 0
memory_clean_frame = 0
character_mask = 0x3F

local function filter_char(char)
    ret_char = char
    if char >= 0x60 then
        ret_char = char & character_mask
    end

    return ret_char
end

local function stack_char(char)
    table.insert(type_buffer, 1, char)
    type_qty = type_qty + 1
end

local function dir(frame)
    stack_char("d")
    stack_char("i")
    stack_char("r")
    stack_char(" ")
    stack_char("0")
    stack_char("\n")
    dir_frame = frame
end

local function is_extension_allowed()
    addr = base_addr + file_index * next_file + base_file_name_size

    ext = {}
    for c = 0, (ext_file_name_size-1) do
        ext[c+1] = mem:read_u8(addr + c)
    end

    allowed_ext = { string.byte('B'), string.byte('A'), string.byte('S')}

    allowed = 0

    for c = 1, 3 do
        if allowed_ext[c] == ext[c] then
            allowed = allowed + 1
        end
    end

    return (allowed == 3)
end

local function run_file()
    print("file index", file_index)
    if is_extension_allowed() == false then
        file_index = file_index + 1
        return
    end

    stack_char("r")
    stack_char("u")
    stack_char("n")
    stack_char("\"")
    for c = 0, base_file_name_size-1 do
        addr = base_addr + file_index * next_file + c
        char = filter_char(mem:read_u8(addr))
        if char ~= 0x20 then
            stack_char(string.char(char))
        end
    end

    stack_char("\"\n")
    try_run = 1
end

local function wait_for_clean_memory(frame)
    if memory_clean_frame ~= 0 then
        if frame > memory_clean_frame + 25 then
            try_run = 0
            dir_frame = 0
            memory_clean_frame = 0
            file_index = file_index + 1
        end
    else
        start_file = mem:read_u8(base_addr + file_index * next_file)
        if start_file == 0 then
            memory_clean_frame = frame
        end
    end
end

local function unstack_char()
    if type_qty > 0 then
        char = table.remove(type_buffer)
        type_qty = type_qty - 1
        emu.keypost(char)
    end
end

frame_num = 0
local function process_frame()
    frame_num = frame_num + 1

    if dir_frame == 0 then
        if frame_num > 90 then
            dir(frame_num)
        end
    else
        if try_run == 0 then
            if frame_num > dir_frame + 350 then
                run_file()
            end
--        else
--            wait_for_clean_memory(frame_num)
        end
    end

    if frame_num % 5 == 0 then
        unstack_char()
    end
end

subscription=emu.add_machine_frame_notifier(process_frame)
