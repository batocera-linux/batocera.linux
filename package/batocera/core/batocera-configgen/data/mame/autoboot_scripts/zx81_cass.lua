button = {}

for i, j in pairs(manager.machine.ioport.ports) do
 for field_name, field in pairs(j.fields) do
  id = field.port.tag .. ',' .. field.mask .. ',' .. field.type
  print(field_name,": ", id)
  button[id] = field
 end
end

local frame_num = 0
local function process_frame()
        frame_num = frame_num + 1

        if frame_num == 200 then
		button[":ROW6,8,49"]:set_value(1) -- J
        elseif frame_num == 205 then
		button[":ROW6,8,49"]:set_value(0) -- J
        elseif frame_num == 215 then
		button[":ROW0,1,49"]:set_value(1) -- shift
		button[":ROW5,1,49"]:set_value(1) -- P
        elseif frame_num == 220 then
		button[":ROW0,1,49"]:set_value(0) -- shift
		button[":ROW5,1,49"]:set_value(0) -- P
        elseif frame_num == 230 then
		button[":ROW0,1,49"]:set_value(1) -- shift
		button[":ROW5,1,49"]:set_value(1) -- P
        elseif frame_num == 235 then
		button[":ROW0,1,49"]:set_value(0) -- shift
		button[":ROW5,1,49"]:set_value(0) -- P
        elseif frame_num == 245 then
		button[":ROW6,1,49"]:set_value(1) -- enter
        elseif frame_num == 250 then
		button[":ROW6,1,49"]:set_value(0) -- enter
        elseif frame_num == 300 then
		manager.machine.cassettes[":cassette"]:play()
        end

       	if manager.machine.cassettes[":cassette"].is_stopped == false and manager.machine.cassettes[":cassette"].motor_state == true then
		    manager.machine.video.throttled = false
		    manager.machine.video.frameskip = 12
		else
		    manager.machine.video.throttled = true
		    manager.machine.video.frameskip = 0
		end
end

subscription=emu.add_machine_frame_notifier(process_frame)
