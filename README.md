# sh3llpass
**Multi-Layer Shellcode Obfuscator & EXE Builder**  
*Çok Katmanlı Shellcode Gizleyici ve EXE Oluşturucu*

---

## 📖 Description / Açıklama

**EN:**  
`sh3llpass` takes raw Meterpreter (or any) shellcode, applies **5 layers of obfuscation** (XOR → RC4 → Byte Swap → Junk Insertion → Delta), and generates a polymorphic C loader. It compiles the loader into a fully functional Windows EXE with built-in **sandbox evasion, debugger detection, and NTDLL unhooking**.  
> ⚠️ For authorized penetration testing and educational use only.

**TR:**  
`sh3llpass`, ham shellcode'u (örn. `msfvenom` ile oluşturulmuş `.raw`) alır, üzerine **5 katmanlı şifreleme/gizleme** (XOR → RC4 → Bayt Değişimi → Junk Ekleme → Delta) uygular ve polimorfik bir C yükleyici oluşturur. Bu yükleyiciyi derleyerek içinde **sanal alan atlatma, hata ayıklayıcı tespiti ve NTDLL unhooking** barındıran bir Windows EXE dosyasına dönüştürür.  
> ⚠️ Yalnızca yetkili sızma testleri ve eğitim amaçlıdır. İzinsiz kullanım yasaktır.


## 📦 Requirements / Gereksinimler

**EN:**  
- Python 3.6+ (only standard libraries used)  
- MinGW-w64 (for automatic compilation)  
  - Ubuntu/Debian: `sudo apt install mingw-w64`  
  - Kali Linux: pre-installed or `sudo apt install mingw-w64`

**TR:**  
- Python 3.6+ (sadece standart kütüphaneler kullanılır)  
- MinGW-w64 (otomatik derleme için)  
  - Ubuntu/Debian: `sudo apt install mingw-w64`  
  - Kali Linux: önceden kuruludur veya `sudo apt install mingw-w64`

---

## Installation / Kurulum

```bash
git clone https://github.com/yourusername/sh3llpass.git
cd sh3llpass
chmod +x sh3llpass.py
