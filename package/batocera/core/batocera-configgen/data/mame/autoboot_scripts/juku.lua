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
		button[":COL.4,8,49"]:set_value(1) -- T
        elseif frame_num == 205 then
		button[":COL.4,8,49"]:set_value(0) -- T

        elseif frame_num == 250 then
		button[":COL.6,32,49"]:set_value(1) -- D
        elseif frame_num == 255 then
		button[":COL.6,32,49"]:set_value(0) -- D

        elseif frame_num == 300 then
		button[":COL.6,32,49"]:set_value(1) -- D
        elseif frame_num == 305 then
		button[":COL.6,32,49"]:set_value(0) -- D

        elseif frame_num == 600 then
		button[":COL.6,32,49"]:set_value(1) -- D
        elseif frame_num == 605 then
		button[":COL.6,32,49"]:set_value(0) -- D

        elseif frame_num == 610 then
		button[":COL.14,8,49"]:set_value(1) -- I
        elseif frame_num == 615 then
		button[":COL.14,8,49"]:set_value(0) -- I

        elseif frame_num == 620 then
		button[":COL.2,8,49"]:set_value(1) -- R
        elseif frame_num == 625 then
		button[":COL.2,8,49"]:set_value(0) -- R

        elseif frame_num == 630 then
		button[":COL.8,32,49"]:set_value(1) -- RETURN
        elseif frame_num == 635 then
		button[":COL.8,32,49"]:set_value(0) -- RETURN

		end
end

subscription=emu.add_machine_frame_notifier(process_frame)
