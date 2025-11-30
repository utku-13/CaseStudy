import os
import sys
import ctypes
from ctypes import c_char_p
import binascii
import base64

#Bu sefer Windows, DLL ararken C:\msys64\mingw64\bin’i de search path’e eklemiş oluyor.
os.add_dll_directory(r"C:\msys64\mingw64\bin")

# 1- base dir detection exe or normal py.
def get_base_dir():
    """
    Returns the directory of:
    - the .py file when running with 'python main.py' (script mode)
    - the .exe file when running the PyInstaller binary (frozen mode)
    """
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller-built EXE
        return os.path.dirname(sys.executable)
    else:
        # Running as a normal Python script
        return os.path.dirname(os.path.abspath(__file__))


base_dir = get_base_dir()

# DLL folder and path (relative to base_dir)
dll_dir = os.path.join(base_dir, "dll_source_file")
dll_path = os.path.join(dll_dir, "functionsfromc.dll")

print(f"Loading DLL from: {dll_path}")
lib = ctypes.CDLL(dll_path)

# 2- since python can not decide what to return we say it is char pointer.
lib.get_hello.restype = c_char_p
lib.get_company_name.restype = c_char_p
lib.get_role.restype = c_char_p
lib.get_system_time.restype = c_char_p
lib.get_image_hex.restype = c_char_p  # fixed "image.png" inside DLL

# Logical function map
functions = {
    "get_hello": lib.get_hello,
    "get_company_name": lib.get_company_name,
    "get_role": lib.get_role,
    "get_system_time": lib.get_system_time,
    "get_image_hex": lib.get_image_hex,
}


# 3- single run normal protocol.
def run_once():
    print("\nExported functions (logical list):")
    for name in functions.keys():
        print(f" - {name}")

    print("\nFunction outputs:")

    image_hex = None

    for name, func in functions.items():
        raw = func()
        if raw is None:
            print(f"{name}() -> returned NULL")
            continue

        text = raw.decode("utf-8", errors="ignore")

        if name == "get_image_hex":
            image_hex = text
            print(f"{name}() -> HEX string (length = {len(text)} characters)")
        else:
            print(f"{name}() -> {text}")

    print("\nReconstructing image from hex and encoding as Base64...")

    if image_hex is None:
        print("ERROR: image_hex is None, get_image_hex() did not run or failed.")
    elif image_hex.startswith("ERROR"):
        print("get_image_hex() returned error from DLL:", image_hex)
    else:
        try:
            # Hex -> raw bytes
            image_bytes = binascii.unhexlify(image_hex)

            # Recovered image path (next to the DLL)
            recovered_path = os.path.join(dll_dir, "recovered_from_hex.png")
            with open(recovered_path, "wb") as f:
                f.write(image_bytes)

            print(f"Recovered image written to: {recovered_path}")

            # Read recovered image and encode as Base64
            with open(recovered_path, "rb") as f:
                data = f.read()

            b64_str = base64.b64encode(data).decode("ascii")

            print("\nBase64 of recovered image:")
            print(b64_str)

        except Exception as e:
            print("Exception while decoding hex or encoding Base64:", e)


# 4- loop logic that our windows service will use.
if __name__ == "__main__":
    import time

    # If "--loop" is passed, run once every 60 seconds (service mode)
    if "--loop" in sys.argv:
        print("Running in LOOP mode (service mode) – updating output every 60 seconds.")
        while True:
            print("\n" + "=" * 60)
            print("New run at:", time.strftime("%Y-%m-%d %H:%M:%S"))
            print("=" * 60)
            run_once()
            time.sleep(60)
    else:
        # Default: single run (developer / manual usage)
        run_once()
