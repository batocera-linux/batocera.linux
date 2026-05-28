local button = {}

for i, j in pairs(manager.machine.ioport.ports) do
 for field_name, field in pairs(j.fields) do
  id = field.port.tag .. ',' .. field.mask .. ',' .. field.type
  print(field_name,"->", id)
  button[id] = field
 end
end


local frame_num = 0
local start_frame = 1000
local function process_frame()
	frame_num = frame_num + 1

	-- Up
	if frame_num == start_frame + 0 then
	    button[":ctrl1:joypad:JOY,4096,51"]:set_value(1)
	elseif frame_num == start_frame + 10 then
	    button[":ctrl1:joypad:JOY,4096,51"]:set_value(0)
	-- Up
	elseif frame_num == start_frame + 20 then
	    button[":ctrl1:joypad:JOY,4096,51"]:set_value(1)
	elseif frame_num == start_frame + 30 then
	    button[":ctrl1:joypad:JOY,4096,51"]:set_value(0)
	-- left
	elseif frame_num == start_frame + 40 then
	    button[":ctrl1:joypad:JOY,16384,53"]:set_value(1)
	elseif frame_num == start_frame + 50 then
	    button[":ctrl1:joypad:JOY,16384,53"]:set_value(0)
	-- Button A
	elseif frame_num == start_frame + 60 then
	    button[":ctrl1:joypad:JOY,1024,64"]:set_value(1)
	elseif frame_num == start_frame + 70 then
	    button[":ctrl1:joypad:JOY,1024,64"]:set_value(0)
	end
end

subscription=emu.add_machine_frame_notifier(process_frame)
