# Case Study Project

This project implements a Windows Service application using Python that interacts with a C++ DLL, processes images, and ensures continuous operation with a self-healing GUI window.

## Project Structure

- `main.py`: Core application logic. Handles both the Windows Service management and the GUI worker process.
- `case_study_app.spec`: PyInstaller specification file for building the standalone executable.
- `install_service.bat`: Batch script for one-click service installation and startup.
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
- Mapped C functions to Python methods with appropriate return types (`c_char_p`).
- Implemented logic to decode the Hex string back to an image file and then re-encode it to Base64.
- Outputs are printed to the console.

### Step 3: Packaging (Exe Compilation)
**Documentation of Packaging Method:**
The application is packaged using **PyInstaller**. To ensure a clean and conflict-free build environment, a dedicated Python virtual environment (`venv`) was used instead of Conda, avoiding common DLL dependency issues.

A custom `.spec` file (`case_study_app.spec`) was created to ensure robustness and include necessary dependencies that are often missed by default builds.

Key configuration details in the `.spec` file:
- **Hidden Imports:** Manually included `win32serviceutil`, `win32service`, `win32event`, `servicemanager` to ensure the Windows Service functions correctly in a standalone environment.
- **Data Inclusion:** The `dll_source_file` directory is bundled directly with the executable to maintain relative path integrity.
- **UAC Admin:** `uac_admin=True` is set to request Administrator privileges automatically, which is required for installing Windows Services.

**Build Command:**
```powershell
pyinstaller case_study_app.spec
```

### Step 4: Windows Service & Persistence
- **Service Architecture:** The application runs as a Windows Service (`CaseStudyService`).
- **GUI Persistence:** Since standard services run in Session 0 (background) and cannot display GUIs directly, the service acts as a "Watchdog".
  - It launches a child process (`--gui-worker` mode) that opens a visible console window.
  - It monitors this child process every 10 seconds.
  - If the user closes the window, the service detects the termination and immediately relaunches it.
- **Auto-Start:** The service is configured to start automatically on system reboot (`--startup auto`).
- **Security:** Only users with Administrator privileges can stop or uninstall the service.

## How to Install and Run

1. **Extract the Package:**
   Ensure the `case_study_app.exe`, `install_service.bat`, and `dll_source_file` folder are in the same directory. (If built from source, they will be in `dist/case_study_app/`).

2. **Install the Service:**
   Right-click on **`install_service.bat`** and select **"Run as Administrator"**.

3. **Verify Operation:**
   - A console window will appear displaying the function outputs and logs.
   - The window will update every 60 seconds.
   - Try closing the window; it will reopen automatically within a few seconds.

4. **Uninstall:**
   To remove the service, run the following command in an Administrator terminal:
   ```bash
   case_study_app.exe remove
   ```

