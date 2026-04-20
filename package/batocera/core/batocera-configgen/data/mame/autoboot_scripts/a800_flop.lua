local button = {}
for key, ports in pairs(manager.machine.ioport.ports) do
	for field_name, field in pairs(ports.fields) do
	    button[field_name] = field
	end
end


local frame_num = 0
local function process_frame()
        frame_num = frame_num + 1

        if frame_num == 1 then
		    button["CONS.2: Option"]:set_value(1)
		end

        if frame_num == 300 then
		    button["CONS.2: Option"]:set_value(0)
		end

end

subscription=emu.add_machine_frame_notifier(process_frame)
