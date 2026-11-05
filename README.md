# Monitor Position

A lightweight Noctalia v5 plugin for arranging monitors on Hyprland. Move a
display to the left, right, above, or below another display, with exact edge
or center alignment even when their resolutions differ.

## Features

- Select the display to move and its reference display.
- Snap to the top, center, or bottom when placing displays side by side.
- Snap to the left, center, or right when placing displays vertically.
- Account for display scaling and rotation.
- Undo the last move while the plugin remains loaded.
- Refresh connected displays whenever the panel opens or on demand.
- Apply changes immediately without saving a fixed monitor layout.

The interface uses buttons and selectors; it does not provide drag and drop.

## Requirements

- Noctalia v5 with plugin API 24 or later.
- Hyprland with the Lua configuration API (`hyprctl eval` and `hl.monitor`).
- Python 3 and `hyprctl` available on `PATH`.
- Two active, non-mirrored displays to arrange.

Tested with Noctalia 5.4.1 and Hyprland 0.57.0. Legacy Hyprland configurations
using the old `hyprctl keyword monitor` interface are not supported.

## Installation

Download or clone this repository. From its root directory, run:

```sh
plugin_dir="${XDG_DATA_HOME:-$HOME/.local/share}/noctalia/plugins/monitor-position"
mkdir -p "$plugin_dir"
cp plugin.toml bar.luau panel.luau monitor.py "$plugin_dir/"
noctalia msg config-reload
noctalia msg plugins enable monitor-tools/monitor-position
```

In Noctalia's bar settings, add the **Monitor Position** widget. Its entry ID
is `monitor-tools/monitor-position:bar`. Existing bar entries can stay as they are.

You can also open the panel directly:

```sh
noctalia msg panel-toggle monitor-tools/monitor-position:panel
```

## Usage

1. Open the monitor icon in the bar.
2. Choose **Monitor to move** and a different display under **Relative to**.
3. Choose **Left**, **Right**, **Above**, or **Below**.
4. Choose the desired **Snap alignment** and press **Apply**.
5. Use **Undo last change** to restore the moved display's previous position.

Only the selected display moves. Other connected displays keep their positions;
with three or more displays, check that your chosen placement does not overlap
another display. Refresh the list after connecting or disconnecting a display.

Changes last for the current compositor session. Reloading the Hyprland
configuration or restarting it may restore its configured layout. The plugin
does not write to the compositor configuration or automatically reapply moves.
Undo keeps one previous position in memory and clears when the plugin unloads.

## Privacy

The plugin runs locally and has no network requests, telemetry, or external
services. Display information comes from the running compositor. No monitor
snapshots, serial numbers, machine-specific paths, credentials, or personal
configuration are bundled in this repository. Layout changes and undo state
are not written to disk by the plugin.

## Development

```sh
noctalia plugins lint .
python3 -m unittest discover -s tests -v
```

`monitor.py` also supports a read-only calculation mode:

```sh
python3 monitor.py plan DISPLAY_TO_MOVE REFERENCE_DISPLAY right center
```

Replace both display placeholders with connected output names. This command
prints the calculated coordinates and current compositor information locally;
it does not move a display. Avoid sharing its raw output if it contains display
details you consider private.

## License

[MIT](LICENSE). Noctalia and Hyprland are separate projects with their own licenses.
