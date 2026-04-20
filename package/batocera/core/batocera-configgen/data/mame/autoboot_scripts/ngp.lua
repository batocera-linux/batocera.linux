local button = {}
local ports = manager.machine.ioport.ports[":Controls"]
for field_name, field in pairs(ports.fields) do
    button[field_name] = field
end

local frame_num = 0
local function process_frame()
	frame_num = frame_num + 1

	if frame_num <  100 * 6  then
		if frame_num % 2 == 0 then
			button["Button A"]:set_value(1)
		else
			button["Button A"]:set_value(0)
		end
	end
end

subscription=emu.add_machine_frame_notifier(process_frame)



