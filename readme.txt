HoleFinder 1.1

Changes:
- Added Hole / Net mode switching
- Pads and vias can now be grouped by drill size or net
- Shows the net name in Hole mode
- Shows the drill size in Net mode
- Improved handling of KiCad IPC connection errors
- Remembers the last window position
- Cross-platform settings location

Settings file:

Windows:
  %LOCALAPPDATA%\HoleFinder\settings.json

Linux:
  $XDG_CONFIG_HOME/HoleFinder/settings.json
  or ~/.config/HoleFinder/settings.json

macOS:
  ~/Library/Application Support/HoleFinder/settings.json

If the saved position is no longer visible on any monitor,
the window opens centered instead.
