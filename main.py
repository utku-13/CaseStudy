import os
import ctypes
from ctypes import c_char_p
import binascii
import base64

#Bu sefer Windows, DLL ararken C:\msys64\mingw64\bin’i de search path’e eklemiş oluyor.
os.add_dll_directory(r"C:\msys64\mingw64\bin")


# 1- DLL kütüphanesini çağırdık.
current_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_dir, "dll_source_file", "functionsfromc.dll")


print(f"Loading DLL from: {dll_path}")
lib = ctypes.CDLL(dll_path)

# 2- Dönenlerin string olduğunu belirtmek için restype ayarı yaptık çünkü python kendisi otomatik yapamıyor.
lib.get_hello.restype = c_char_p
lib.get_company_name.restype = c_char_p
lib.get_role.restype = c_char_p
lib.get_system_time.restype = c_char_p
lib.get_image_hex.restype = c_char_p

# 3- Kütüphane içindeki fonksiyonları listeledik, bunun için dictionary kullandık.
functions = {
    "get_hello": lib.get_hello,
    "get_company_name": lib.get_company_name,
    "get_role": lib.get_role,
    "get_system_time": lib.get_system_time,
    "get_image_hex": lib.get_image_hex,
}

print("\nExported functions (logical list):")
for name in functions.keys():
    print(f" - {name}")

# 4- Listelediğiniz fonksiyonları çağırıp çıktıları ekrana yazıyoruz.
print("\nFunction outputs:")

image_hex = None  # get_image_hex sonucunu burada saklayacağız

for name, func in functions.items():
    raw = func()  # C tarafı const char* döndürüyor -> ctypes bunu bytes yapar
    if raw is None:
        print(f"{name}() -> returned NULL")
        continue

    text = raw.decode("utf-8", errors="ignore")

    if name == "get_image_hex":
        image_hex = text
        print(f"{name}() -> HEX string (length = {len(text)} characters)")
    else:
        print(f"{name}() -> {text}")

# 5- Görsel verisini hex formatından decode edip, base64'e çeviriyoruz.
print("\nReconstructing image from hex and encoding as base64...")

if image_hex is None:
    print("ERROR: image_hex is None, get_image_hex() did not run or failed.")
elif image_hex.startswith("ERROR"):
    print("get_image_hex() returned error from DLL:", image_hex)
else:
    try:
        # Hex string -> raw bytes (decode kısmı)
        image_bytes = binascii.unhexlify(image_hex)

        # Dosyaya yazıp görseli elde et (ör: recovered_from_hex.png)
        recovered_path = os.path.join(current_dir, "recovered_from_hex.png")
        with open(recovered_path, "wb") as f:
            f.write(image_bytes)

        print(f"Recovered image written to: {recovered_path}")

        # Şimdi bu elde edilen görseli base64 ile encode et
        with open(recovered_path, "rb") as f:
            data = f.read()

        b64_str = base64.b64encode(data).decode("ascii")

        # Base64 değerini ekrana bas
        print("\nBase64 of recovered image:")
        print(b64_str)

    except Exception as e:
        print("Exception while decoding hex or encoding base64:", e)
