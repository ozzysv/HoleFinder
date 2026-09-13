HoleFinder 1.0

Changes:
- remembers the last window position
- cross-platform settings location

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
