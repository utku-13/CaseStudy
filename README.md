# Case Study Project

This project implements a Windows Service application using Python that interacts with a C++ DLL, processes images, and ensures continuous operation with a self-healing GUI window.

## Project Structure

- `main.py`: Core application logic. Handles both the Windows Service management and the GUI worker process via Task Scheduler integration.
- `case_study_app.spec`: PyInstaller specification file for building the standalone executable.
- `install_service.bat`: Batch script for one-click service installation and Task setup.
- `uninstall_service.bat`: Script to remove the service and clean up tasks.
- `dll_source_file/`: Directory containing the C++ source code, compiled DLL (`functionsfromc.dll`), and image assets.

## Requirements

- Windows OS (Windows 10/11 recommended)
- Python 3.x (for development/building)
- Libraries: `pywin32`, `pyinstaller`

## Step-by-Step Implementation Details

### Step 1: C++ DLL Creation
- Three string-returning functions were implemented in C++.
- A system time function was added.
- An image encoding function (Hexadecimal) was implemented.
- Compiled into `functionsfromc.dll`.

### Step 2: Python & DLL Integration
- Loaded the DLL using Python's `ctypes` library.
- Mapped C functions to Python methods with appropriate return types.
- Implemented logic to decode the Hex string back to an image file and then re-encode it to Base64.

### Step 3: Packaging (Exe Compilation)
**Documentation of Packaging Method:**
The application is packaged using **PyInstaller**. To ensure a clean and conflict-free build environment, a dedicated Python virtual environment (`venv`) was used instead of Conda, avoiding common DLL dependency issues.

A custom `.spec` file was configured to:
- Manually include hidden imports like `win32serviceutil` and `servicemanager`.
- Bundle the `dll_source_file` directory directly with the executable.
- Request Administrator privileges (`uac_admin=True`).

**Build Command:**
```powershell
pyinstaller case_study_app.spec
```

### Step 4: Windows Service & GUI Persistence (The "Watchdog" Architecture)
To strictly fulfill the requirement of **"displaying output to the screen"** while running as a Windows Service, I engineered a specific solution to handle **Windows Session 0 Isolation**.

Since standard Windows Services run in a background session (Session 0) and cannot display GUIs to the user, I implemented a **Task Scheduler Bridge**:

1.  **Service (Patron):** Runs in the background as `SYSTEM`. It does not perform the logic itself but acts as a **Watchdog**. It checks if the worker process is running every 10 seconds.
2.  **Worker (GUI):** Instead of launching the process directly (which would be invisible), the Service triggers a **Windows Scheduled Task**. This task is configured to run the `.exe` in the active user's session, ensuring the console window is visible on the desktop.
3.  **Self-Healing:** If the user manually closes the console window, the Service detects the process termination and immediately re-triggers the task, restoring the window.
4.  **Logging:** As a fail-safe, outputs are mirrored to both the console and a log file (`service_output.txt`).

## How to Install and Run

1. **Build the Project:**
   Run `pyinstaller case_study_app.spec`. This will create a `dist/case_study_app` directory.

2. **One-Click Install:**
   Run **`install_service.bat`** as Administrator (located in the project root).
   - This installs the Windows Service.
   - It creates the necessary Scheduled Task for GUI interaction.
   - It starts the service immediately.

3. **Verify Operation:**
   - A console window should appear on your desktop displaying the function outputs.
   - If the window is closed, it will reopen automatically.
   - Logs can also be viewed in `dist/case_study_app/service_output.txt`.

4. **Uninstall:**
   Run **`uninstall_service.bat`** as Administrator to remove the service and the scheduled task.
