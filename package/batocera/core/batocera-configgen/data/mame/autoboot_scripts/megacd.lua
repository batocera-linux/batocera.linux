button = {}

for i, j in pairs(manager.machine.ioport.ports) do
 for field_name, field in pairs(j.fields) do
  id = field.port.tag .. ',' .. field.mask .. ',' .. field.type
  print(field_name,": ", id)
  button[id] = field
 end
end

frame_num=0
function process_frame()
        frame_num = frame_num + 1

        if frame_num == 1 then
		-- P1 start
		button[":ctrl1:mdpad:PAD,128,46"]:set_value(1)
        end
        if frame_num == 40 then
		button[":ctrl1:mdpad:PAD,128,46"]:set_value(0)
        end
        if frame_num == 80 then
		-- P1 start
		button[":ctrl1:mdpad:PAD,128,46"]:set_value(1)
        end
        if frame_num == 120 then
		button[":ctrl1:mdpad:PAD,128,46"]:set_value(0)
        end
end

subscription = emu.add_machine_frame_notifier(process_frame)

