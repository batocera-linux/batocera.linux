cpu = manager.machine.devices[":maincpu"]
mem = cpu.spaces["program"]
base_addr = 0x9E7D
base_file_name_size = 8
ext_file_name_size = 3
next_file = 14
file_index = 0
cat_frame = 0
try_run = 0
type_buffer = {}
type_qty = 0
memory_clean_frame = 0

local function stack_char(char)
    table.insert(type_buffer, 1, char)
    type_qty = type_qty + 1
end

local function cat(frame)
    stack_char("c")
    stack_char("a")
    stack_char("t")
    stack_char("\n")
    cat_frame = frame
end

local function is_extension_allowed()
    addr = base_addr + file_index * next_file + base_file_name_size

    ext = {}
    for c = 0, 2 do
        ext[c+1] = mem:read_u8(addr + c) & 0x7F
    end

    forbidden_ext = { string.byte('T'), string.byte('X'), string.byte('T')}

    allowed = 0

    for c = 1, 3 do
        if forbidden_ext[c] ~= ext[c] then
            allowed = 1
            break
        end
    end

    return allowed
end


local function run_file()
    if is_extension_allowed() == 0 then
        file_index = file_index + 1
        return
    end

    stack_char("r")
    stack_char("u")
    stack_char("n")
    stack_char("\"")
    for c = 0, base_file_name_size-1 do
        addr = base_addr + file_index * next_file + c
        char = mem:read_u8(addr)
        if char ~= 0x20 then
            char = char & 0x7F
            stack_char(string.char(char))
        end
    end

    stack_char("\n")
    try_run = 1
end

local function wait_for_clean_memory(frame)
    if memory_clean_frame ~= 0 then
        if frame > memory_clean_frame + 25 then
            try_run = 0
            cat_frame = 0
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

    if cat_frame == 0 then
        if frame_num > 250 then
            cat(frame_num)
        end
    else
        if try_run == 0 then
            if frame_num > cat_frame + 250 then
                run_file()
            end
        else
            wait_for_clean_memory(frame_num)
        end
    end

    if frame_num % 5 == 0 then
        unstack_char()
    end
end

emu.keypost("|disc\n")
emu.keypost("run\"disc\n")
subscription=emu.add_machine_frame_notifier(process_frame)
