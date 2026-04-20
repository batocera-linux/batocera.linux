local frame_num = 0
local throttle_asked = 0
local throttle_qty = 0
local command

local function process_frame()
    frame_num = frame_num + 1

    --if manager.machine.cassettes[":cas_hack"].is_stopped == false and manager.machine.cassettes[":cas_hack"].motor_state == true then
    --    if throttle_asked == 0 then
    --        throttle_qty = throttle_qty + 1
    --        throttle_asked = 1

    --        manager.machine.video.throttled = false
    --        manager.machine.video.frameskip = 12
    --    end
    --else
    --    if throttle_asked == 1 then
    --        throttle_asked = 0

    --        manager.machine.video.throttled = true
    --        manager.machine.video.frameskip = 0

    --        emu.keypost("RUN\n")
    --    end
    --end

    if frame_num == 200 then
        print("Mode: ",command_mode)
        emu.keypost(command_mode)
    elseif frame_num == 250 then
        print("Page: ",command_page)
        emu.keypost(command_page)
    elseif frame_num == 300 then
        emu.keypost("CLOAD\n")
    end
end

command_page = ''
command_mode = ''

info_usage = os.getenv("RANDOMAME_INFO_USAGE")
if info_usage ~= nil and info_usage ~= "" then
    if string.find(info_usage, "Page 1") then
        command_page = "1\n"
    elseif string.find(info_usage, "Page 2") then
        command_page = "2\n"
    elseif string.find(info_usage, "Page 3") then
        command_page = "3\n"
    elseif string.find(info_usage, "Page 4") then
        command_page = "4\n"
    end

    if string.find(info_usage, "Mode 1") then
        command_mode = "1"
    elseif string.find(info_usage, "Mode 2") then
        command_mode = "2"
    elseif string.find(info_usage, "Mode 3") then
        command_mode = "3"
    elseif string.find(info_usage, "Mode 4") then
        command_mode = "4"
    elseif string.find(info_usage, "Mode 5") then
        command_mode = "5"
    end
end

subscription=emu.add_machine_frame_notifier(process_frame)
