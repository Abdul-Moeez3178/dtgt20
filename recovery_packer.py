# By Mehraan
"""
recovery_packer.py - Custom Recovery Ramdisk Patcher and Repacking Engine for Infinix X6871
Automates injecting optimized configs, KeyMint decrypt overlays, and system properties overrides into prebuilt recovery images.
"""

import os
import sys
import shutil
import subprocess
import datetime
import hashlib

class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def show_banner():
    print(Color.HEADER + Color.BOLD + "=" * 70 + Color.END)
    print(Color.CYAN + Color.BOLD + "    ____                                      ____             __             " + Color.END)
    print(Color.CYAN + Color.BOLD + "   / __ \\___  _________  _   _____  _______  / __ \\____ ______/ /_____  _____" + Color.END)
    print(Color.CYAN + Color.BOLD + "  / /_/ / _ \\/ ___/ __ \\| | / / _ \\/ ___/ / / /_/ / __ `/ ___/ //_/ _ \\/ ___/" + Color.END)
    print(Color.CYAN + Color.BOLD + " / _, _/  __/ /__/ /_/ /| |/ /  __/ /  / /_/ / ____/ /_/ / /__/ ,< /  __/ /    " + Color.END)
    print(Color.CYAN + Color.BOLD + "/_/ |_|\\___/\\___/\\____/ |___/\\___/_/   \\__, /_/    \\__,_/\\___/_/|_|\\___/_/     " + Color.END)
    print(Color.CYAN + Color.BOLD + "                                      /____/                                  " + Color.END)
    print(Color.BLUE + Color.BOLD + "    Infinix GT 20 Pro (X6871) Ramdisk Overlay Patcher & Repacker Engine" + Color.END)
    print(Color.BLUE + "                        Author: Mehraan Edition                       " + Color.END)
    print(Color.HEADER + Color.BOLD + "=" * 70 + Color.END)

def calculate_checksum(file_path, algo="sha256"):
    h = hashlib.new(algo)
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "Unknown"

def patch_cpio(input_path, output_path, patches, prop_overrides):
    with open(input_path, 'rb') as f:
        data = f.read()
    
    out_f = open(output_path, 'wb')
    idx = 0
    while idx < len(data):
        magic = data[idx:idx+6]
        if magic != b'070701' and magic != b'070702':
            # Find next magic (skip padding)
            next_idx = data.find(b'070701', idx)
            if next_idx == -1:
                next_idx = data.find(b'070702', idx)
            if next_idx == -1:
                out_f.write(data[idx:])
                break
            out_f.write(data[idx:next_idx])
            idx = next_idx
            magic = data[idx:idx+6]

        header = data[idx:idx+110]
        filesize = int(header[54:62], 16)
        namesize = int(header[94:102], 16)
        
        name = data[idx+110:idx+110+namesize-1].decode('utf-8', errors='ignore')
        
        name_pad = (110 + namesize) % 4
        name_pad_len = 4 - name_pad if name_pad != 0 else 0
        
        content_start = idx + 110 + namesize + name_pad_len
        content = data[content_start:content_start+filesize]
        
        content_pad = filesize % 4
        content_pad_len = 4 - content_pad if content_pad != 0 else 0
        
        new_content = None
        # Clean path match
        clean_name = name.strip('/')
        
        if clean_name in patches:
            print(Color.GREEN + f"  [x] Injecting customized source: {clean_name}" + Color.END)
            with open(patches[clean_name], 'rb') as pf:
                new_content = pf.read()
        elif clean_name in ['prop.default', 'default.prop']:
            print(Color.GREEN + f"  [x] Injecting prop overrides into: {clean_name}" + Color.END)
            stock_props = content.decode('utf-8', errors='ignore')
            lines = stock_props.splitlines()
            # Overlay overrides
            for key, val in prop_overrides.items():
                lines = [line for line in lines if not line.strip().startswith(f"{key}=")]
                lines.append(f"{key}={val}")
            new_content = "\n".join(lines).encode('utf-8')
            
        if new_content is not None:
            new_size = len(new_content)
            new_size_hex = f"{new_size:08x}".encode('utf-8')
            new_header = header[:54] + new_size_hex + header[62:]
            
            out_f.write(new_header)
            out_f.write(data[idx+110:content_start])
            out_f.write(new_content)
            
            new_content_pad = new_size % 4
            new_content_pad_len = 4 - new_content_pad if new_content_pad != 0 else 0
            out_f.write(b'\x00' * new_content_pad_len)
        else:
            total_entry_len = 110 + namesize + name_pad_len + filesize + content_pad_len
            out_f.write(data[idx:idx+total_entry_len])
            
        idx += 110 + namesize + name_pad_len + filesize + content_pad_len
        
    out_f.close()

def parse_system_prop(prop_path):
    overrides = {}
    if os.path.exists(prop_path):
        with open(prop_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    parts = line.split('=', 1)
                    overrides[parts[0].strip()] = parts[1].strip()
    return overrides

def main():
    show_banner()
    
    # Paths configuration
    proj_root = os.path.dirname(os.path.abspath(__file__))
    aik_dir = r"C:\Users\Adnan\Downloads\TWRPGEN"
    out_dir = r"C:\Users\Adnan\Videos\recovery"
    
    # Config overrides mapping
    patches = {
        "init.recovery.mt6895.rc": os.path.join(proj_root, "device_tree", "init.recovery.mt6895.rc"),
        "init.tee.rc": os.path.join(proj_root, "device_tree", "init.tee.rc"),
        "system/etc/recovery.fstab": os.path.join(proj_root, "device_tree", "recovery.fstab"),
        "first_stage_ramdisk/fstab.mt6895": os.path.join(proj_root, "device_tree", "recovery.fstab"),
        "system/etc/twrp.flags": os.path.join(proj_root, "device_tree", "twrp.flags"),
        "vendor.goodix.rc": os.path.join(proj_root, "device_tree", "vendor.goodix.rc")
    }
    
    prop_overrides = parse_system_prop(os.path.join(proj_root, "device_tree", "system.prop"))
    
    # Clean output target folder
    os.makedirs(out_dir, exist_ok=True)
    
    targets = [
        {"name": "TWRP-X6871-Unofficial-Patched.img", "src": "TWRP-X6871-20260306_UNOFFICIAL.img"},
        {"name": "OrangeFox-X6871-Unofficial-Patched.img", "src": "OrangeFox-R12.0_20260508_15.1.2-Unofficial-X6871.img"}
    ]
    
    for target in targets:
        print(Color.BOLD + f"\n[+] Processing Recovery Image: {target['src']} -> {target['name']}" + Color.END)
        
        # 1. Unpack Image
        print("[+] Unpacking original image...")
        subprocess.run(["cmd.exe", "/c", "magiskboot.exe cleanup"], cwd=aik_dir, capture_output=True)
        
        res = subprocess.run(["cmd.exe", "/c", f"magiskboot.exe unpack {target['src']}"], cwd=aik_dir, capture_output=True, text=True)
        if res.returncode != 0:
            print(Color.RED + f"[-] Error: Failed to unpack {target['src']}" + Color.END)
            print(res.stderr)
            continue
            
        ramdisk_path = os.path.join(aik_dir, "ramdisk.cpio")
        if not os.path.exists(ramdisk_path):
            print(Color.RED + "[-] Error: ramdisk.cpio was not generated after unpack." + Color.END)
            continue
            
        # 2. Decompress LZ4 ramdisk in WSL
        print("[+] Decompressing ramdisk LZ4 archive stream inside WSL...")
        decomp_path = os.path.join(aik_dir, "ramdisk_decomp.cpio")
        if os.path.exists(decomp_path):
            os.remove(decomp_path)
            
        wsl_res = subprocess.run([
            "wsl", "lz4", "-d", "-q", "-f",
            f"/mnt/c/Users/Adnan/Downloads/TWRPGEN/ramdisk.cpio", 
            f"/mnt/c/Users/Adnan/Downloads/TWRPGEN/ramdisk_decomp.cpio"
        ], capture_output=True)
        
        if wsl_res.returncode != 0 or not os.path.exists(decomp_path):
            print(Color.RED + "[-] Error: Failed to decompress ramdisk LZ4 stream in WSL." + Color.END)
            continue
            
        # 3. Patch decompressed CPIO contents
        print("[+] Executing Python CPIO header patching engine...")
        patched_path = os.path.join(aik_dir, "ramdisk_patched.cpio")
        patch_cpio(decomp_path, patched_path, patches, prop_overrides)
        
        # 4. Recompress CPIO to LZ4 in WSL
        print("[+] Re-compressing ramdisk to LZ4 format inside WSL...")
        if os.path.exists(ramdisk_path):
            os.remove(ramdisk_path)
            
        # Standard GKI LZ4 format (-l -1 legacy header)
        wsl_comp = subprocess.run([
            "wsl", "lz4", "-l", "-1", "-q", "-f",
            f"/mnt/c/Users/Adnan/Downloads/TWRPGEN/ramdisk_patched.cpio",
            f"/mnt/c/Users/Adnan/Downloads/TWRPGEN/ramdisk.cpio"
        ], capture_output=True)
        
        if wsl_comp.returncode != 0 or not os.path.exists(ramdisk_path):
            print(Color.RED + "[-] Error: Failed to recompress ramdisk to LZ4 inside WSL." + Color.END)
            continue
            
        # Remove temporary CPIO files
        os.remove(decomp_path)
        os.remove(patched_path)
        
        # 5. Repack Image
        print("[+] Repacking image components into recovery vendor_boot.img...")
        repack_res = subprocess.run(["cmd.exe", "/c", f"magiskboot.exe repack {target['src']} new-boot.img"], cwd=aik_dir, capture_output=True, text=True)
        new_boot_path = os.path.join(aik_dir, "new-boot.img")
        
        if not os.path.exists(new_boot_path):
            print(Color.RED + "[-] Error: Failed to repack image. new-boot.img was not generated." + Color.END)
            print(repack_res.stdout)
            print(repack_res.stderr)
            continue
            
        # 6. Copy output to final location
        dest_path = os.path.join(out_dir, target['name'])
        shutil.copy2(new_boot_path, dest_path)
        print(Color.GREEN + f"[+] SUCCESS: Patched custom recovery deployed!" + Color.END)
        print(Color.BOLD + f"  [*] Path: {dest_path}" + Color.END)
        print(f"  [*] Size: {os.path.getsize(dest_path) / (1024*1024):.2f} MB")
        print(f"  [*] SHA256 Checksum: {calculate_checksum(dest_path)}" + Color.END)
        
        # Cleanup temporary files
        subprocess.run(["cmd.exe", "/c", "magiskboot.exe cleanup"], cwd=aik_dir, capture_output=True)

    print(Color.GREEN + "\n[+] Recovery repacking and deployment process finished successfully!" + Color.END)

if __name__ == "__main__":
    main()
