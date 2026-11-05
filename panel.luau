local monitors = {}
local target, reference = nil, nil
local side, alignment = "right", "center"
local previous = nil
local busy = false
local message = ""
local render

local function request(args, done)
  if busy then return end
  busy = true
  render()
  local argv = {"python3", noctalia.pluginDir() .. "/monitor.py"}
  for _, arg in ipairs(args) do table.insert(argv, arg) end
  local accepted = noctalia.runAsync(argv, function(result)
    busy = false
    local data = noctalia.json.decode(result.stdout or "")
    if result.exitCode ~= 0 or data == nil then
      message = "Error: " .. (result.stderr or "invalid response")
    else
      monitors = data.monitors or {}
      local names = {}
      for _, m in ipairs(monitors) do names[m.name] = true end
      if not names[reference] then
        reference = monitors[1] and monitors[1].name
        for _, m in ipairs(monitors) do
          if string.sub(m.name, 1, 3) == "eDP" then reference = m.name end
        end
      end
      if not names[target] or target == reference then
        target = nil
        for _, m in ipairs(monitors) do if m.name ~= reference then target = m.name; break end end
      end
      if done then done(data) end
    end
    render()
  end)
  if not accepted then busy = false; message = "Unable to launch the monitor helper"; render() end
end

local function choice(text, value, current, action)
  return ui.button({text = text, selected = value == current,
    variant = value == current and "primary" or "outline", enabled = not busy, onClick = action})
end

render = function()
  local options, ti, ri = {}, 0, 0
  local details = {}
  for i, m in ipairs(monitors) do
    table.insert(options, m.name .. " · " .. m.logicalWidth .. "×" .. m.logicalHeight)
    if m.name == target then ti = i - 1 end
    if m.name == reference then ri = i - 1 end
    table.insert(details, m.name .. "   " .. m.x .. ", " .. m.y)
  end
  local horizontal = side == "left" or side == "right"
  panel.render(ui.column({gap = 12, padding = 20}, {
    ui.row({justify = "space_between", align = "center"}, {
      ui.label({text = "Monitor Position", fontSize = 22, fontWeight = "bold"}),
      ui.button({glyph = "refresh", tooltip = "Refresh monitors", enabled = not busy, onClick = function() request({"list"}) end}),
      ui.button({glyph = "close", onClick = function() panel.close() end}),
    }),
    ui.label({text = "Monitor to move"}),
    ui.select({key = "target-" .. tostring(target), options = options, selectedIndex = ti, enabled = not busy, onChange = function(index)
      local m = monitors[(tonumber(index) or 0) + 1]; if m then target = m.name; render() end
    end}),
    ui.label({text = "Relative to"}),
    ui.select({key = "reference-" .. tostring(reference), options = options, selectedIndex = ri, enabled = not busy, onChange = function(index)
      local m = monitors[(tonumber(index) or 0) + 1]; if m then reference = m.name; render() end
    end}),
    ui.row({gap = 6, justify = "center"}, {
      choice("← Left", "left", side, function() side = "left"; render() end),
      choice("Right →", "right", side, function() side = "right"; render() end),
      choice("↑ Above", "above", side, function() side = "above"; render() end),
      choice("↓ Below", "below", side, function() side = "below"; render() end),
    }),
    ui.label({text = "Snap alignment"}),
    ui.row({gap = 8, justify = "center"}, {
      choice(horizontal and "Top" or "Left", "start", alignment, function() alignment = "start"; render() end),
      choice("Center", "center", alignment, function() alignment = "center"; render() end),
      choice(horizontal and "Bottom" or "Right", "end", alignment, function() alignment = "end"; render() end),
    }),
    ui.label({text = #monitors < 2 and "Connect a second monitor to arrange displays." or table.concat(details, "  ·  "), fontSize = 12, color = "on_surface_variant"}),
    ui.label({text = message ~= "" and message or "Changes apply to the current session only.", fontSize = 13, maxLines = 2}),
    ui.row({gap = 8, justify = "space_between"}, {
      ui.button({text = "Undo last change", enabled = previous ~= nil and not busy, onClick = function()
        request({"restore", noctalia.json.encode(previous)}, function() previous = nil; message = "Previous arrangement restored." end)
      end}),
      ui.button({text = busy and "Please wait…" or "Apply", variant = "primary", enabled = not busy and target ~= nil and reference ~= nil and target ~= reference, onClick = function()
        request({"move", target, reference, side, alignment}, function(data)
          previous = data.previous; message = "Arrangement applied."
        end)
      end}),
    }),
  }))
end

function onOpen()
  message = ""
  request({"list"})
end
function update() render() end
