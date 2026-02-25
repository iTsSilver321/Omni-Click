# Product Requirements Document (PRD): Advanced Autoclicker

## 1. Product Overview
**Product Name:** OmniClick
**Objective:** To create a standalone Windows executable (`.exe`) autoclicker that provides users with precise control over their clicking rate (CPS), custom keybindings, and flexible activation modes (Toggle vs. Hold), all wrapped in a modern, intuitive Graphical User Interface (GUI).

## 2. Target Audience
* **Gamers:** Needing repetitive clicking for idle games, Minecraft, or RPGs.
* **Professionals/Testers:** Requiring automated clicks for software testing or repetitive data entry tasks.

## 3. Core Functional Requirements

### 3.1. Click Rate Control (CPS)
* **Requirement:** The user must be able to define the exact Clicks Per Second (CPS).
* **Acceptance Criteria:**
    * Input field allowing values between 1 and 100+ CPS.
    * Optional: A visual slider bound to the input field for easy adjustment.
    * The software calculates the exact millisecond delay between clicks based on the CPS (Delay = 1000 / CPS).

### 3.2. Activation Modes
* **Requirement:** The software must support two distinct operational modes.
* **Acceptance Criteria:**
    * **Autonomous (Toggle) Mode:** Pressing the designated hotkey starts the clicking loop. Pressing it again stops it.
    * **Hold-to-Click Mode:** The autoclicker only executes clicks while the designated hotkey (or mouse button) is actively held down. Clicking stops immediately upon release.

### 3.3. Custom Keybinding (Hotkeys)
* **Requirement:** Users must be able to set custom keys to start/stop the autoclicker.
* **Acceptance Criteria:**
    * A "Listen" button in the UI that captures the next key pressed by the user and sets it as the active hotkey (e.g., `F6`, `Mouse Button 4`).
    * The hotkey listener must operate globally (working in the background even when the autoclicker UI is minimized).

### 3.4. Click Type Selection (Optional but Recommended)
* **Requirement:** Choose which mouse button is being simulated.
* **Acceptance Criteria:** Dropdown menu to select Left Click, Right Click, or Middle Click.

## 4. User Interface & User Experience (UI/UX)

The UI should be clean, modern, and avoid the "clunky Windows 95" look common to older autoclickers.

| UI Component | Description |
| :--- | :--- |
| **Main Window** | Small, fixed-size window. Cannot be maximized to prevent UI stretching. "Always on top" toggle option. |
| **Theme** | Default Dark Mode with high-contrast accent colors (e.g., neon green for "Active", dark grey for idle). |
| **Status Indicator** | A clear visual indicator (Text or LED-style circle) showing if the autoclicker is currently **Running** or **Stopped**. |
| **Mode Selector** | Radio buttons or a sleek toggle switch to select between "Toggle" and "Hold" modes. |
| **CPS Input** | A large, readable text box centered on the screen, accompanied by a horizontal slider. |

## 5. Technical Specifications & Tech Stack

To achieve the `.exe` format and a nice UI, here are the two best development paths:

### Option A: Python (Recommended for fast prototyping)
* **Logic:** `pyautogui` or `pynput` for mouse control and global keyboard hooking.
* **UI Framework:** `CustomTkinter` or `PyQt6` (for modern, dark-themed UIs).
* **Executable Generation:** `PyInstaller` or `Auto-py-to-exe` to bundle the Python script into a single standalone `.exe` file.

### Option B: C# / .NET (Recommended for lowest latency and native Windows feel)
* **Logic:** Standard Windows API (`user32.dll`) imports for mouse events and global keyboard hooks.
* **UI Framework:** Windows Presentation Foundation (WPF) with a modern UI library like *MaterialDesignInXAML*.
* **Executable Generation:** Compiles natively to `.exe` via Visual Studio.

## 6. Out of Scope (V2 Features)
* Macro recording (recording mouse movements).
* Randomized CPS (adding slight random delays to bypass anti-cheat software).
* Specific screen coordinate clicking.