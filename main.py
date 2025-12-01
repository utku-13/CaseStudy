import os
import sys
import ctypes
from ctypes import c_char_p
import binascii
import base64
import time
import subprocess

os.add_dll_directory(r"C:\msys64\mingw64\bin")

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
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def worker_gui_loop():
    base_dir = get_base_dir()
    dll_dir = os.path.join(base_dir, "dll_source_file")
    dll_path = os.path.join(dll_dir, "functionsfromc.dll")

    if os.name == 'nt':
        os.environ["PATH"] = dll_dir + ";" + os.environ["PATH"]
        try:
            os.add_dll_directory(dll_dir)
            os.add_dll_directory(r"C:\msys64\mingw64\bin")
        except:
            pass

    # Loglama fonksiyonu
    log_file = os.path.join(base_dir, "service_output.txt")
    def log_print(msg):
        print(msg)
        try:
            with open(log_file, "a") as f:
                f.write(msg + "\n")
        except:
            pass

    try:
        lib = ctypes.CDLL(dll_path)
        lib.get_hello.restype = c_char_p
        lib.get_company_name.restype = c_char_p
        lib.get_role.restype = c_char_p
        lib.get_system_time.restype = c_char_p
        lib.get_image_hex.restype = c_char_p
    except Exception as e:
        log_print(f"DLL Yükleme Hatası: {e}")
        time.sleep(10)
        return

    functions = {
        "get_hello": lib.get_hello,
        "get_company_name": lib.get_company_name,
        "get_role": lib.get_role,
        "get_system_time": lib.get_system_time,
        "get_image_hex": lib.get_image_hex,
    }

    log_print("=== Case Study Worker Started ===")
    log_print(f"Logs are being written to: {log_file}")
    log_print("Bu pencere CaseStudyService tarafından yönetilmektedir.")
    log_print("Kapatırsanız servis tarafından tekrar açılacaktır.\n")

    while True:
        log_print("\n" + "=" * 60)
        log_print("Time: " + time.strftime("%Y-%m-%d %H:%M:%S"))
        log_print("=" * 60)

        image_hex = None
        for name, func in functions.items():
            try:
                raw = func()
                if raw:
                    text = raw.decode("utf-8", errors="ignore")
                    if name == "get_image_hex":
                        image_hex = text
                        log_print(f"{name}() -> HEX string (len={len(text)})")
                    else:
                        log_print(f"{name}() -> {text}")
                else:
                    log_print(f"{name}() -> NULL")
            except Exception as ex:
                log_print(f"Hata ({name}): {ex}")

        if image_hex and not image_hex.startswith("ERROR"):
            try:
                image_bytes = binascii.unhexlify(image_hex)
                recovered_path = os.path.join(dll_dir, "recovered_from_hex.png")
                with open(recovered_path, "wb") as f:
                    f.write(image_bytes)
                log_print(f"Image saved: {recovered_path}")
            except Exception as e:
                log_print(f"Image Error: {e}")

        log_print("\nBir sonraki güncelleme için 60 saniye bekleniyor...")
        time.sleep(60)


# --- 2. Windows Service Sınıfı (Patron) ---

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CaseStudyService"
    _svc_display_name_ = "Case Study App Service"
    _svc_description_ = "GUI penceresini yöneten servis."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        # Servis dururken GUI görevini de durdurmayi deneyebiliriz
        # ama GUI kullanicinin oldugu icin dokunmamak daha iyi olabilir.
        # Istenirse 'taskkill' ile oldurulebilir.
        try:
            subprocess.run('taskkill /F /FI "IMAGENAME eq case_study_app.exe" /FI "SESSION NE 0"', shell=True)
        except:
            pass

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main_loop()

    def main_loop(self):
        # Bu servis artik subprocess.Popen yapmiyor.
        # Onun yerine Task Scheduler'i tetikliyor.
        
        while self.running:
            # 1. Kontrol: GUI Worker calisiyor mu?
            # 'tasklist' komutuyla calisan processleri kontrol ediyoruz.
            # Session 0 (Services) disindaki case_study_app.exe'leri ariyoruz.
            try:
                output = subprocess.check_output('tasklist /FI "IMAGENAME eq case_study_app.exe" /FI "SESSION NE 0"', shell=True)
                
                # Eger process listesinde exe adimiz yoksa, calismiyor demektir.
                if b"case_study_app.exe" not in output:
                    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                          0xF000,
                                          ("GUI Worker kapali, Task Scheduler ile baslatiliyor...", ''))
                    
                    # Task Scheduler gorevini calistir
                    subprocess.run('schtasks /Run /TN "CaseStudyWorker"', shell=True)
                
            except Exception as e:
                servicemanager.LogErrorMsg(f"Process kontrol hatasi: {e}")

            # 10 saniye bekle
            rc = win32event.WaitForSingleObject(self.hWaitStop, 10000)
            if rc == win32event.WAIT_OBJECT_0:
                break


# --- 3. Entry Point ---

if __name__ == '__main__':
    if "--gui-worker" in sys.argv:
        worker_gui_loop()
    
    elif len(sys.argv) > 1:
        if os.name == 'nt':
            win32serviceutil.HandleCommandLine(AppService)
        else:
            print("Service komutlari sadece Windows'ta calisir.")

    else:
        if os.name == 'nt':
            try:
                servicemanager.Initialize()
                servicemanager.PrepareToHostSingle(AppService)
                servicemanager.StartServiceCtrlDispatcher()
            except Exception:
                print("Servis modunda baslatilamadi, normal test modunda calisiyor...")
                try:
                    worker_gui_loop()
                except KeyboardInterrupt:
                    pass
        else:
            worker_gui_loop()