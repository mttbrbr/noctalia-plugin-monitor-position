"""Runtime-only Hyprland monitor positioning. Never writes compositor config."""
import json
import math
import subprocess
import sys


def hypr(*args):
    p = subprocess.run(["hyprctl", *args], capture_output=True, text=True, timeout=5)
    if p.returncode:
        raise ValueError(p.stderr.strip() or p.stdout.strip() or "Hyprland is unavailable")
    return p.stdout


def monitors():
    return [m for m in json.loads(hypr("monitors", "-j"))
            if not m.get("disabled") and m.get("mirrorOf", "none") in ("none", "")]


def size(m):
    w, h = m["width"], m["height"]
    if m.get("transform", 0) % 2:
        w, h = h, w
    return round(w / m["scale"]), round(h / m["scale"])


def position(target, reference, side, align):
    if side not in ("left", "right", "above", "below") or align not in ("start", "center", "end"):
        raise ValueError("Invalid position or alignment")
    tw, th = size(target)
    rw, rh = size(reference)
    x, y = reference["x"], reference["y"]
    fraction = {"start": 0, "center": .5, "end": 1}[align]
    if side in ("left", "right"):
        return x - tw if side == "left" else x + rw, y + math.floor((rh - th) * fraction)
    return x + math.floor((rw - tw) * fraction), y - th if side == "above" else y + rh


def move(m, x, y):
    name = m["name"]
    if any(c in name for c in ",;\n"):
        raise ValueError("Invalid monitor name")
    mode = f'{m["width"]}x{m["height"]}@{m["refreshRate"]:.5f}'
    # JSON string escaping is also valid for these Lua string literals.
    rule = ('hl.monitor({ output = ' + json.dumps(name) + ', mode = '
            + json.dumps(mode) + ', position = ' + json.dumps(f'{int(x)}x{int(y)}')
            + f', scale = {float(m["scale"])}, transform = {int(m.get("transform", 0))}' + ' })')
    result = hypr("eval", rule)
    if result.strip().lower() not in ("ok", ""):
        raise ValueError(result.strip())


def main(args):
    current = monitors()
    by_name = {m["name"]: m for m in current}
    result = {}
    if args[0] in ("move", "plan"):
        _, target, reference, side, align = args
        if target == reference:
            raise ValueError("Choose two different monitors")
        if target not in by_name or reference not in by_name:
            raise ValueError("Monitor disconnected: refresh the list")
        x, y = position(by_name[target], by_name[reference], side, align)
        result["previous"] = {"name": target, "x": by_name[target]["x"], "y": by_name[target]["y"]}
        result["position"] = [x, y]
        if args[0] == "move":
            move(by_name[target], x, y)
            current = monitors()
    elif args[0] == "restore":
        previous = json.loads(args[1])
        if previous["name"] not in by_name:
            raise ValueError("The monitor to restore is disconnected")
        move(by_name[previous["name"]], previous["x"], previous["y"])
        current = monitors()
    elif args != ["list"]:
        raise ValueError("Invalid command")
    result["monitors"] = [dict(m, logicalWidth=size(m)[0], logicalHeight=size(m)[1]) for m in current]
    return result


if __name__ == "__main__":
    try:
        print(json.dumps(main(sys.argv[1:])))
    except (ValueError, KeyError, subprocess.SubprocessError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
