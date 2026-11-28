-- an onboard output without jack sensing loses to one with a detected connection

log = Log.open_topic ("s-default-nodes")

cutils = require ("common-utils")
nutils = require ("node-utils")

function routeAvailability (node_props, devices_om)
  local card_profile_device = tonumber (node_props ["card.profile.device"])
  local device_id = node_props ["device.id"]
  if not card_profile_device or not device_id then
    return nil
  end

  local device = devices_om:lookup {
    Constraint { "bound-id", "=", device_id, type = "gobject" },
  }
  if not device or device.properties ["device.bus"] ~= "pci" then
    return nil
  end

  for p in device:iterate_params ("Route") do
    local route = cutils.parseParam (p, "Route")
    if route and route.device == card_profile_device then
      return route.available
    end
  end
  return nil
end

SimpleEventHook {
  name = "default-nodes/demote-undetected-sinks",
  before = { "default-nodes/find-selected-default-node",
             "default-nodes/find-best-default-node" },
  interests = {
    EventInterest {
      Constraint { "event.type", "=", "select-default-node" },
      Constraint { "default-node.type", "=", "audio.sink" },
    },
  },
  execute = function (event)
    local available_nodes = event:get_data ("available-nodes")
    available_nodes = available_nodes and available_nodes:parse ()
    if not available_nodes then
      return
    end

    local devices_om = cutils.get_object_manager ("device")
    local detected = false
    local undetected = {}

    for _, node_props in ipairs (available_nodes) do
      local available = routeAvailability (node_props, devices_om)
      if available == "yes" then
        detected = true
      elseif available == "unknown" then
        table.insert (undetected, node_props)
      end
    end

    if not detected or #undetected == 0 then
      return
    end

    for _, node_props in ipairs (undetected) do
      node_props ["priority.session"] = nutils.get_session_priority (node_props) - 10000
      log:info ("demoting " .. node_props ["node.name"] .. ", no jack detection")
    end

    local nodes = {}
    for _, node_props in ipairs (available_nodes) do
      table.insert (nodes, Json.Object (node_props))
    end
    event:set_data ("available-nodes", Json.Array (nodes))
  end
}:register ()
