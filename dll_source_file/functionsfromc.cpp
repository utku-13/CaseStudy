#include <string>
#include <chrono>
#include <ctime>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <iterator>

extern "C" {

    // 1- Basit string dönen fonksiyon
    __declspec(dllexport) const char* get_hello() {
        static std::string result = "ilk String, Selamlar ";
        return result.c_str();
    }

    // 2- ikinci string döndüren fonksiyon
    __declspec(dllexport) const char* get_company_name() {
        static std::string result = "İkinci String, Firma Adı: Turkish Technology";
        return result.c_str();
    }

    // 3- Üçüncü string döndüren fonksiyon
    __declspec(dllexport) const char* get_role() {
        static std::string result = "Üçüncü String, Rol: Python Developer";
        return result.c_str();
    }

    // 4- Sistem saati
    __declspec(dllexport) const char* get_system_time() {
        using namespace std::chrono;

        static std::string result;

        auto now = system_clock::now();
        std::time_t tt = system_clock::to_time_t(now);
        std::tm local_tm{};

        // Windows için güvenli localtime
        localtime_s(&local_tm, &tt);

        std::ostringstream oss;
        oss << std::put_time(&local_tm, "%Y-%m-%d %H:%M:%S");
        result = oss.str();

        return result.c_str();
    }

    // 5- Görseli okuyup hexadecimal string döndüren fonksiyon
    __declspec(dllexport) const char* get_image_hex() {
        static std::string hexResult;
        const char* filename = "dll_source_file/smallpng.png";  // Seçtiğin görselin adı

        std::ifstream file(filename, std::ios::binary);
        if (!file) {
            hexResult = "ERROR: cannot open image file.";
            return hexResult.c_str();
        }

        // Dosyanın tüm byte'larını oku
        std::vector<unsigned char> buffer(
            (std::istreambuf_iterator<char>(file)),
            std::istreambuf_iterator<char>()
        );

        std::ostringstream oss;
        oss << std::hex << std::uppercase << std::setfill('0');

        for (unsigned char b : buffer) {
            oss << std::setw(2) << static_cast<int>(b);
        }

        hexResult = oss.str();
        return hexResult.c_str();
    }

} 
