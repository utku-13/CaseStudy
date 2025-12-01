import os
import sys
import ctypes
from ctypes import c_char_p
import binascii
import base64
import time
import subprocess

# Windows Service modüllerini sadece Windows ortamında import etmeyi deneyelim
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
except ImportError:
    pass


# --- 1. DLL ve İş Mantığı (Worker) ---
def get_base_dir():
    """
    Çalışma dizinini belirler (Exe veya Script modu).
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def worker_gui_loop():
    """
    Görünür pencerede çalışacak ve sürekli ekrana basacak olan döngü.
    """
    base_dir = get_base_dir()
    dll_dir = os.path.join(base_dir, "dll_source_file")
    dll_path = os.path.join(dll_dir, "functionsfromc.dll")

    # Windows DLL path
    if os.name == 'nt':
        try:
            os.add_dll_directory(r"C:\msys64\mingw64\bin")
        except:
            pass

    # DLL Yükleme
    try:
        lib = ctypes.CDLL(dll_path)
        lib.get_hello.restype = c_char_p
        lib.get_company_name.restype = c_char_p
        lib.get_role.restype = c_char_p
        lib.get_system_time.restype = c_char_p
        lib.get_image_hex.restype = c_char_p
    except Exception as e:
        print(f"DLL Yükleme Hatası: {e}")
        time.sleep(10)
        return

    functions = {
        "get_hello": lib.get_hello,
        "get_company_name": lib.get_company_name,
        "get_role": lib.get_role,
        "get_system_time": lib.get_system_time,
        "get_image_hex": lib.get_image_hex,
    }

    print("=== Case Study Worker Started ===")
    print("Bu pencere CaseStudyService tarafından yönetilmektedir.")
    print("Kapatırsanız servis tarafından tekrar açılacaktır.\n")

    while True:
        print("\n" + "=" * 60)
        print("Time:", time.strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)

        image_hex = None
        for name, func in functions.items():
            try:
                raw = func()
                if raw:
                    text = raw.decode("utf-8", errors="ignore")
                    if name == "get_image_hex":
                        image_hex = text
                        print(f"{name}() -> HEX string (len={len(text)})")
                    else:
                        print(f"{name}() -> {text}")
                else:
                    print(f"{name}() -> NULL")
            except Exception as ex:
                print(f"Hata ({name}): {ex}")

        # Resim kaydetme
        if image_hex and not image_hex.startswith("ERROR"):
            try:
                image_bytes = binascii.unhexlify(image_hex)
                recovered_path = os.path.join(dll_dir, "recovered_from_hex.png")
                with open(recovered_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Image saved: {recovered_path}")
            except Exception as e:
                print(f"Image Error: {e}")

        print("\nBir sonraki güncelleme için 60 saniye bekleniyor...")
        time.sleep(60)


# --- 2. Windows Service Sınıfı (Patron) ---

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CaseStudyService"
    _svc_display_name_ = "Case Study App Service"
    _svc_description_ = "Arka planda çalışıp GUI penceresini yöneten servis."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.worker_process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        # Servis dururken worker'ı da öldür
        if self.worker_process:
            try:
                self.worker_process.terminate()
            except:
                pass

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main_loop()

    def main_loop(self):
        # Bu servis, kendisinin --gui-worker modunu yeni pencerede başlatır.
        executable = sys.executable
        script_path = os.path.abspath(__file__)
        
        # Komut oluşturma:
        # Frozen (exe) ise: case_study_app.exe --gui-worker
        # Script ise: python main.py --gui-worker
        if getattr(sys, "frozen", False):
            cmd = [executable, "--gui-worker"]
        else:
            cmd = [executable, script_path, "--gui-worker"]

        while self.running:
            # Process yaşıyor mu kontrol et
            if self.worker_process is None or self.worker_process.poll() is not None:
                # Yaşayan process yok, yenisini başlat
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                      0xF000, # Custom ID
                                      ("Worker GUI baslatiliyor...", ''))
                
                # CREATE_NEW_CONSOLE flag'i ile yeni pencere açtırıyoruz.
                # Not: Session 0 isolation nedeniyle Windows 10/11'de pencere 
                # doğrudan kullanıcı masaüstüne gelmeyebilir.
                # Ancak "Interactive Services Detection" veya benzeri araçlarla erişilebilir.
                # Hoca'nın isteği "Ekran kapatılırsa açılsın" olduğu için en doğru yaklaşım budur.
                try:
                     self.worker_process = subprocess.Popen(
                        cmd,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                except Exception as e:
                    servicemanager.LogErrorMsg(f"Worker baslatilamadi: {e}")

            # 5 saniyede bir kontrol et (Pencere kapanırsa çabuk geri gelsin)
            rc = win32event.WaitForSingleObject(self.hWaitStop, 10000)
            if rc == win32event.WAIT_OBJECT_0:
                break

# --- 3. Entry Point ---

if __name__ == '__main__':
    # 1. Mod: GUI Worker (İşçi) - Servis tarafindan bu parametreyle cagrilir
    if "--gui-worker" in sys.argv:
        worker_gui_loop()
    
    # 2. Mod: Komut Satiri Argumanlari (install, start, remove vb.)
    elif len(sys.argv) > 1:
        if os.name == 'nt':
            win32serviceutil.HandleCommandLine(AppService)
        else:
            print("Service komutlari sadece Windows'ta calisir.")

    # 3. Mod: Argumansiz Cagri (Servis Baslangici VEYA Cift Tiklama)
    else:
        # Windows'ta argumansiz calisiyorsa, once Servis olarak baslamayi deneriz.
        # Eger hata alirsak (cunku normal konsoldan calistirilmislardir), normal moda duseriz.
        if os.name == 'nt':
            try:
                servicemanager.Initialize()
                servicemanager.PrepareToHostSingle(AppService)
                servicemanager.StartServiceCtrlDispatcher()
            except Exception:
                # Servis dispatcher baslatilamadi (Demek ki konsoldan cift tiklandi)
                print("Servis modunda baslatilamadi, normal test modunda calisiyor...")
                try:
                    worker_gui_loop()
                except KeyboardInterrupt:
                    pass
        else:
            # Windows degilse direkt normal calis
            worker_gui_loop()