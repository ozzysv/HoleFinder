# HoleFinder

**HoleFinder** is a KiCad 10 IPC plugin for inspecting drilled holes
on a PCB by drill size and quickly locating pads and vias on the board.

![KiCad](https://img.shields.io/badge/KiCad-10.x-blue)
![Version](https://img.shields.io/badge/version-1.0-green)
![License](https://img.shields.io/badge/license-GPL--3.0-blue)



## Demo

<img src="doc/test1.gif" width="800"/> 

## Features

-   Groups drilled objects by hole size
-   Supports round and obround holes
-   Detects drilled pads and vias
-   Shows the number of objects for each drill size
-   Displays pad reference and pad number
-   Quickly locates the selected pad or via on the PCB
-   Centers the KiCad view on the selected object
-   Blinks the selected object for easier identification
-   Double-click an item to locate it
-   **Update** button refreshes the hole list from the current board
-   Remembers the last window position
-   Prevents multiple HoleFinder instances from running at the same
    time
-   Cross-platform settings storage
-   Built using the modern KiCad IPC API (`kicad-python` / `kipy`)

## Requirements

-   KiCad 10.x
-   Python 3.9 or newer
-   `kicad-python >= 0.8.0`
-   `wxPython ~= 4.2`

Dependencies are listed in `requirements.txt`.

## Installation

### Manual installation

Copy the HoleFinder plugin folder into the KiCad user plugins
directory.

**Windows**

``` text
%USERPROFILE%\Documents\KiCad\10.0\plugins\HoleFinder
```

The resulting structure should look like:

``` text
HoleFinder/
├── plugin.json
├── requirements.txt
├── HoleFinder_action.py
├── HoleFinder_core.py
├── HoleFinder_24.png
├── HoleFinder_32.png
├── HoleFinder_48.png
└── HoleFinder_64.png
```

Restart the PCB Editor or refresh the plugins after installation.

## Usage

1.  Open a PCB in KiCad PCB Editor.
2.  Start **HoleFinder** from the plugin toolbar/menu.
3.  Select a hole size from the **Hole** list.
4.  Select a pad or via from **List of Objects**.
5.  Click **Locate**, or double-click the object.
6.  KiCad centers the view on the object and briefly blinks its
    selection.
7.  Click **Update** after modifying the PCB to rebuild the list.

## Settings

HoleFinder remembers the last window position.

Settings are stored outside the plugin directory so they are preserved
when the plugin is updated.

**Windows**

``` text
%LOCALAPPDATA%\HoleFinder\settings.json
```

**Linux**

``` text
$XDG_CONFIG_HOME/HoleFinder/settings.json
```

or, if `XDG_CONFIG_HOME` is not defined:

``` text
~/.config/HoleFinder/settings.json
```

**macOS**

``` text
~/Library/Application Support/HoleFinder/settings.json
```

If the saved window position is no longer visible on any connected
display, HoleFinder opens centered.

## KiCad IPC API

HoleFinder uses the modern KiCad IPC API rather than the legacy SWIG
`pcbnew` Python API.

Main Python package:

``` text
kicad-python
```

The plugin communicates with the currently running KiCad PCB Editor
through `kipy`.

## Version

Current version: **1.0**


## License

This project is licensed under the **GNU General Public License v3.0
(GPL-3.0)**.

See the `LICENSE` file for the full license text.
