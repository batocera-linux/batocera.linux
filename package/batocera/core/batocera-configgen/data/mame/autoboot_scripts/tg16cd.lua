local button = {}

for i, j in pairs(manager.machine.ioport.ports) do
 for field_name, field in pairs(j.fields) do
  id = field.port.tag .. ',' .. field.mask .. ',' .. field.type
  print(field_name,"->", id)
  button[id] = field
 end
end


local frame_num = 0
local function process_frame()
	frame_num = frame_num + 1

	if frame_num == 25 then
        button[":ctrl:joypad2_turbo:BUTTONS,8,46"]:set_value(1)
	elseif frame_num == 30 then
	    button[":ctrl:joypad2_turbo:BUTTONS,8,46"]:set_value(0)
	end
end

subscription=emu.add_machine_frame_notifier(process_frame)



