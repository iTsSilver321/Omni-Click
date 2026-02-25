# ⚡ OmniClick

OmniClick is an advanced, highly customizable autoclicker built with Python and `customtkinter`. It features a modern, dark-themed UI and provides precise control over clicking behavior, effects, targeting, and hotkeys.

## ✨ Features

- **Dynamic CPS Control**: Set a fixed CPS (Clicks Per Second) or enable a random CPS range (min/max) for a more human-like clicking speed.
- **Multiple Click Types**: Supports Left, Right, and Middle clicks.
- **Toggle & Hold Modes**:
  - `Toggle`: Press the hotkey once to start clicking, and again to stop.
  - `Hold`: The autoclicker only runs while you are physically holding down the mouse button.
- **Humanization & Effects**:
  - **Humanize**: Adds a randomized percentage deviation to the click delay.
  - **Jitter**: Adds random cursor movement (in pixels) while clicking.
- **Advanced Automation**:
  - **Clicks per Event**: Send double or triple clicks per interval.
  - **Burst Mode**: Clicks a specific number of times, then pauses for a set duration before resuming.
  - **Multi-Location Clicking**: Define specific coordinates for the clicker to sequence through.
  - **Click Limits**: Stop automatically after a certain number of clicks or a set run duration.
  - **Start Delay**: Adds a delay before the clicker starts.
- **Per-App Window Targeting**: Enter a window title (substring), and the clicker will *only* execute clicks if that specific window is currently in focus.
- **Global Hotkeys**: Configure hotkeys to Start/Stop the clicker, cycle the Click Type, or cycle the Mode (Toggle/Hold).
- **System Tray Integration**: Can be minimized to the system tray for background operation.

## 🚀 How to Use

### Prerequisites

Ensure you have Python 3 installed. Install the dependencies using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Running the Application

Run the main application script:

```bash
python main.py
```

*(Alternatively, you can build a standalone executable using `python build.py` if PyInstaller is configured.)*

### General Usage

1. **Main Tab**: Configure your core CPS settings. Use the slider or entry boxes to set the exact speed. Switch between Toggle/Hold modes and select the mouse button to click.
2. **Effects Tab**: Add Jitter (cursor shaking) and adjust the Humanize percentage to bypass basic click-speed detection.
3. **Advanced Tab**: 
   - Enter a target application name in **Window Target** to isolate clicks to that specific app.
   - Configure burst clicking, limitations (duration or total clicks), and delays.
4. **Keybinds Tab**: Click "Listen" next to an action and press any key to set it as your global hotkey.
5. **Start Clicking**: Press your designated `Start/Stop` hotkey (default is `F6`), or click the Start button on the Main tab.

## ⚙️ Settings

Settings are automatically saved to a local configuration file when you close the application and reloaded on your next startup.
