function update()
  barWidget.render(ui.glyph({name = "device-desktop", size = 20}))
  barWidget.setTooltip("Monitor Position")
end
function onClick()
  noctalia.togglePanel("monitor-tools/monitor-position:panel")
end
