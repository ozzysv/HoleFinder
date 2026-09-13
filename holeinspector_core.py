import wx
import wx.adv
import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from kipy import KiCad

NM_PER_MM = 1_000_000.0
PLUGIN_DIR = Path(__file__).resolve().parent

def get_config_dir():
    """Return a cross-platform user config directory for HoleInspector."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        path = Path(base) if base else (Path.home() / "AppData" / "Local")
        path = path / "HoleInspector"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "HoleInspector"
    else:
        base = os.environ.get("XDG_CONFIG_HOME")
        path = Path(base) if base else (Path.home() / ".config")
        path = path / "HoleInspector"

    path.mkdir(parents=True, exist_ok=True)
    return path

def get_settings_path():
    return get_config_dir() / "settings.json"

def load_settings():
    try:
        with get_settings_path().open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_settings(data):
    try:
        with get_settings_path().open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def mm_text(nm):
    return f"{nm / NM_PER_MM:.4f}".rstrip("0").rstrip(".")

def id_key(obj):
    """Return a stable string key for a KiCad API object id."""
    try:
        return str(obj.id)
    except Exception:
        return ""

def footprint_reference(fp):
    """Read the footprint reference, e.g. U3 / J1."""
    try:
        return str(fp.reference_field.text.value)
    except Exception:
        try:
            return str(fp.reference_field.text)
        except Exception:
            return "?"

class HoleInspectorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="HoleInspector 1.0", size=(280, 500))
        self.kicad = KiCad()
        self.board = self.kicad.get_board()
        self.groups = {}
        self.items = []
        self._blink_generation = 0

        try:
            icon = wx.Icon(str(PLUGIN_DIR / "holeinspector_32.png"), wx.BITMAP_TYPE_PNG)
            self.SetIcon(icon)
        except Exception:
            pass

        panel = wx.Panel(self)
        main = wx.BoxSizer(wx.VERTICAL)

        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(wx.StaticText(panel, label="Hole:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.combo = wx.Choice(panel)
        row.Add(self.combo, 1, wx.EXPAND)
        main.Add(row, 0, wx.EXPAND | wx.ALL, 10)

        main.Add(wx.StaticText(panel, label="List of Objects:"), 0, wx.LEFT | wx.RIGHT, 10)

        self.listbox = wx.ListBox(panel)
        main.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_update = wx.Button(panel, label="Update")
        self.btn_locate = wx.Button(panel, label="Locate")
        self.btn_close = wx.Button(panel, label="Close")
        buttons.Add(self.btn_update, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer()
        buttons.Add(self.btn_locate, 0, wx.RIGHT, 8)
        buttons.Add(self.btn_close, 0)
        main.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.status = wx.StaticText(panel, label="")
        main.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.github_link = wx.adv.HyperlinkCtrl(
            panel,
            label="github.com/ozzysv/HoleInspector",
            url="https://github.com/ozzysv/HoleInspector",
        )
        main.Add(self.github_link, 0, wx.ALIGN_CENTER | wx.ALL, 8)

        panel.SetSizer(main)

        self.combo.Bind(wx.EVT_CHOICE, self.on_group)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.on_locate)
        self.btn_update.Bind(wx.EVT_BUTTON, self.on_update)
        self.btn_locate.Bind(wx.EVT_BUTTON, self.on_locate)
        self.btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.restore_window_position()
        self.refresh()

    def restore_window_position(self):
        """Restore the last window position if it is still visible on a display."""
        settings = load_settings()

        try:
            x = int(settings["window_x"])
            y = int(settings["window_y"])
        except Exception:
            self.Centre()
            return

        rect = wx.Rect(x, y, self.GetSize().width, self.GetSize().height)

        visible = False
        for i in range(wx.Display.GetCount()):
            display_rect = wx.Display(i).GetClientArea()
            if display_rect.Intersects(rect):
                visible = True
                break

        if visible:
            self.SetPosition((x, y))
        else:
            self.Centre()

    def save_window_position(self):
        """Save only the current top-left window position."""
        try:
            pos = self.GetPosition()
            settings = load_settings()
            settings["window_x"] = int(pos.x)
            settings["window_y"] = int(pos.y)
            save_settings(settings)
        except Exception:
            pass

    def build_pad_reference_map(self):
        """
        Build pad UUID -> footprint reference map.
        This avoids relying only on pad.number, which may repeat across footprints.
        """
        result = {}
        try:
            for fp in self.board.get_footprints():
                ref = footprint_reference(fp)
                try:
                    pads = fp.definition.pads
                except Exception:
                    pads = []
                for pad in pads:
                    key = id_key(pad)
                    if key:
                        result[key] = ref
        except Exception:
            pass
        return result

    def collect(self):
        holes = []
        pad_refs = self.build_pad_reference_map()

        # PTH / NPTH pads with drill.
        for pad in self.board.get_pads():
            try:
                drill = pad.padstack.drill.diameter
                dx, dy = int(drill.x), int(drill.y)
                if dx <= 0 or dy <= 0:
                    continue

                pos = pad.position
                number = str(getattr(pad, "number", "?"))
                ref = pad_refs.get(id_key(pad), "?")
                label = f"Pad {ref}:{number}" if ref != "?" else f"Pad {number}"

                holes.append(
                    (dx, dy, label, pad, int(pos.x), int(pos.y))
                )
            except Exception:
                continue

        # Vias.
        for i, via in enumerate(self.board.get_vias(), 1):
            try:
                d = int(via.drill_diameter)
                if d <= 0:
                    continue
                pos = via.position
                holes.append(
                    (d, d, f"Via {i}", via, int(pos.x), int(pos.y))
                )
            except Exception:
                continue

        return holes

    def refresh(self):
        self._blink_generation += 1
        self.board = self.kicad.get_board()
        holes = self.collect()

        grouped = defaultdict(list)
        for h in holes:
            grouped[(h[0], h[1])].append(h)

        self.groups = {}
        labels = []

        for key in sorted(grouped, key=lambda k: (max(k), min(k))):
            dx, dy = key
            items = grouped[key]

            if dx == dy:
                name = f"Round {mm_text(dx)} mm"
            else:
                name = f"Obround {mm_text(dx)} x {mm_text(dy)} mm"

            label = f"{name} ({len(items)})"
            labels.append(label)
            self.groups[label] = items

        self.combo.Set(labels)

        if labels:
            self.combo.SetSelection(0)
            self.load_group(labels[0])
        else:
            self.listbox.Clear()
            self.items = []

        self.status.SetLabel(f"{len(holes)} drilled objects / {len(labels)} sizes")

    def load_group(self, label):
        self._blink_generation += 1
        self.items = self.groups.get(label, [])
        self.listbox.Set([x[2] for x in self.items])

        if self.items:
            self.listbox.SetSelection(0)

    def on_group(self, evt):
        self.load_group(self.combo.GetStringSelection())

    def on_update(self, evt):
        try:
            self.refresh()
        except Exception as e:
            wx.MessageBox(str(e), "HoleInspector", wx.OK | wx.ICON_ERROR)

    def select_item(self, item, selected):
        try:
            if selected:
                self.board.add_to_selection(item)
            else:
                self.board.remove_from_selection(item)
        except Exception:
            pass

    def start_blink(self, item):
        """
        Blink by toggling KiCad selection several times.
        A generation token prevents an older timer sequence from continuing
        after the user selects another object.
        """
        self._blink_generation += 1
        generation = self._blink_generation

        def step(index):
            if generation != self._blink_generation:
                return

            # Six toggles, ending selected.
            selected = (index % 2 == 0)
            self.select_item(item, selected)

            if index < 5:
                wx.CallLater(180, step, index + 1)
            else:
                self.select_item(item, True)

        step(0)

    def center_selection(self):
        """
        Ask KiCad to pan the PCB view to the selected object.
        This action name is an internal KiCad TOOL_ACTION, so failure is ignored.
        """
        try:
            self.kicad.run_action("common.Control.centerSelection")
            return True
        except Exception:
            return False

    def on_locate(self, evt):
        idx = self.listbox.GetSelection()
        if idx == wx.NOT_FOUND or idx >= len(self.items):
            return

        h = self.items[idx]

        try:
            self._blink_generation += 1
            self.board.clear_selection()
            self.board.add_to_selection(h[3])

            centered = self.center_selection()
            self.start_blink(h[3])

            suffix = "" if centered else "   (selected)"
            self.status.SetLabel(
                f"{h[2]}   X={mm_text(h[4])} mm   Y={mm_text(h[5])} mm{suffix}"
            )
        except Exception as e:
            wx.MessageBox(f"Locate failed:\n{e}", "HoleInspector", wx.OK | wx.ICON_ERROR)

    def on_close(self, evt):
        self._blink_generation += 1
        self.save_window_position()
        try:
            self.kicad.close()
        except Exception:
            pass
        self.Destroy()

def run():
    app = wx.App(False)

    # Cross-platform single-instance guard.
    # Keep the checker alive for the entire lifetime of the plugin.
    checker = wx.SingleInstanceChecker(f"HoleInspector-{wx.GetUserId()}")

    if checker.IsAnotherRunning():
        wx.MessageBox(
            "HoleInspector is already running.",
            "HoleInspector",
            wx.OK | wx.ICON_INFORMATION,
        )
        return

    frame = HoleInspectorFrame()
    frame._single_instance_checker = checker
    frame.Show()
    app.MainLoop()
