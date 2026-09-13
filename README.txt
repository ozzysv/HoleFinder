HoleInspector 1.0

Changes:
- remembers the last window position
- cross-platform settings location

Settings file:
Windows:
  %LOCALAPPDATA%\HoleInspector\settings.json

Linux:
  $XDG_CONFIG_HOME/HoleInspector/settings.json
  or ~/.config/HoleInspector/settings.json

macOS:
  ~/Library/Application Support/HoleInspector/settings.json

If the saved position is no longer visible on any monitor,
the window opens centered instead.

Changes in v0.9.9:
- prevents launching more than one HoleInspector window at the same time
- uses wx.SingleInstanceChecker (cross-platform)
- a second launch shows "HoleInspector is already running."

Changes in 1.0:
- replaced toolbar/plugin icons with the new 24/32/48/64 px icons
- added visible version number 1.0
- window title is now "HoleInspector 1.0"
