local io_base = {}

function io_base.get()
    button = {}
    for i, j in pairs(manager.machine.ioport.ports) do
     for field_name, field in pairs(j.fields) do
      --print(field_name)
      --print("  tag", field.port.tag)
      --print("  mask", field.mask)
      --print("  type", field.type)
      id = field.port.tag .. ',' .. field.mask .. ',' .. field.type
      print(field_name,'=',id)
      button[id] = field
     end
    end
    return button
end

return io_base
