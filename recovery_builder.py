# By Mehraan
"""
recovery_builder.py - High-Performance Automated Recovery Build Engine for Infinix GT 20 Pro (X6871)
Automates workspace synchronization, dependency mapping, source updates, and compilation under WSL/Linux.
"""

import os
import sys
import shutil
import subprocess
import argparse
import platform
import datetime
import hashlib

# ANSI Escape Sequences for Premium Text Aesthetics
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def show_banner():
    """Renders the sleek, premium M1 Recovery Builder startup banner."""
    print(Color.HEADER + Color.BOLD + "=" * 70 + Color.END)
    print(Color.CYAN + Color.BOLD + "    ____                                      ____        _ __     __ " + Color.END)
    print(Color.CYAN + Color.BOLD + "   / __ \\___  _________  _   _____  _______  / __ )__  __(_) /____/ /_" + Color.END)
    print(Color.CYAN + Color.BOLD + "  / /_/ / _ \\/ ___/ __ \\| | / / _ \\/ ___/ / / __  / / / / / / __  / _ \\" + Color.END)
    print(Color.CYAN + Color.BOLD + " / _, _/  __/ /__/ /_/ /| |/ /  __/ /  / /_/ /_/ / /_/ / / / /_/ /  __/" + Color.END)
    print(Color.CYAN + Color.BOLD + "/_/ |_|\\___/\\___/\\____/ |___/\\___/_/   \\__, /_____/\\__,_/_/_/\\__,_/\\___/ " + Color.END)
    print(Color.CYAN + Color.BOLD + "                                      /____/                          " + Color.END)
    print(Color.BLUE + Color.BOLD + "    Infinix GT 20 Pro (X6871) Unified Compilation Automation Engine" + Color.END)
    print(Color.BLUE + "                        Author: Mehraan Edition                       " + Color.END)
    print(Color.HEADER + Color.BOLD + "=" * 70 + Color.END)

def convert_win_path_to_wsl(win_path):
    """Converts a standard Windows file path to a WSL mount path."""
    if not win_path:
        return ""
    # Remove quotes
    win_path = win_path.strip('\'"')
    # Check if it has a drive letter
    if len(win_path) >= 2 and win_path[1] == ':':
        drive = win_path[0].lower()
        parts = win_path[2:].replace('\\', '/').split('/')
        wsl_path = f"/mnt/{drive}/" + "/".join(p for p in parts if p)
        return wsl_path
    return win_path.replace('\\', '/')

def calculate_checksum(file_path, algo="sha256"):
    """Calculates the checksum of a compiled binary file."""
    h = hashlib.new(algo)
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "Unknown"

def run_wsl_command(command, cwd=None):
    """Runs a command inside WSL and streams the output stdout/stderr."""
    # Check if WSL is available
    try:
        wsl_check = subprocess.run(["wsl", "echo", "1"], capture_output=True, text=True)
        if wsl_check.returncode != 0:
            print(Color.RED + "[-] Error: WSL is not configured or running on this Windows host." + Color.END)
            return False
    except FileNotFoundError:
        print(Color.RED + "[-] Error: wsl executable not found in PATH." + Color.END)
        return False

    wsl_cwd = convert_win_path_to_wsl(cwd) if cwd else None
    
    # Construct WSL command line
    wsl_cmd = ["wsl"]
    if wsl_cwd:
        wsl_cmd += ["--cd", wsl_cwd]
    
    # Run bash command
    wsl_cmd += ["bash", "-c", command]
    
    print(Color.BLUE + f"[+] Executing WSL: {command}" + Color.END)
    try:
        process = subprocess.Popen(wsl_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(Color.RED + f"[-] Subprocess runtime crash: {e}" + Color.END)
        return False

def run_native_command(command, cwd=None):
    """Runs a command natively on Linux and streams output."""
    print(Color.BLUE + f"[+] Executing shell: {command}" + Color.END)
    try:
        process = subprocess.Popen(["bash", "-c", command], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(Color.RED + f"[-] Subprocess runtime crash: {e}" + Color.END)
        return False

def deploy_tree_sources(src_dir, dest_manifest_dir, is_wsl):
    """Copies workspace device tree files into AOSP workspace tree."""
    print(Color.BOLD + "\n[+] Syncing and Deploying Device Tree source files..." + Color.END)
    
    # Verify local source folders
    local_dt = os.path.join(src_dir, "device_tree")
    local_pb = os.path.join(src_dir, "prebuilts")
    
    if not os.path.exists(local_dt) or not os.path.exists(local_pb):
        print(Color.RED + f"[-] Source paths do not exist. Checked: {local_dt} & {local_pb}" + Color.END)
        return False
        
    # Set targets
    target_dt = os.path.join(dest_manifest_dir, "device", "infinix", "X6871")
    target_pb = os.path.join(target_dt, "prebuilt")
    
    try:
        # Recreate target folders
        if os.path.exists(target_dt):
            print(Color.YELLOW + f"  [!] Cleaning existing device tree folder: {target_dt}" + Color.END)
            shutil.rmtree(target_dt)
        os.makedirs(target_pb, exist_ok=True)
        
        # Copy configuration files
        print(Color.GREEN + "  [x] Copying device configs..." + Color.END)
        for item in os.listdir(local_dt):
            s = os.path.join(local_dt, item)
            d = os.path.join(target_dt, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
                
        # Copy kernel and modules prebuilts
        print(Color.GREEN + "  [x] Copying prebuilt GKI kernel & modules..." + Color.END)
        shutil.copy2(os.path.join(local_pb, "prebuilt_kernel"), os.path.join(target_pb, "kernel"))
        shutil.copy2(os.path.join(local_pb, "prebuilt_dtb"), os.path.join(target_pb, "dtb"))
        shutil.copy2(os.path.join(local_pb, "prebuilt_dtbo.img"), os.path.join(target_pb, "dtbo.img"))
        
        for mod in ["adaptive-ts.ko", "gt9886.ko", "gt9896s.ko", "gt9916_common.ko", "richtap_haptic_hv.ko"]:
            src_mod = os.path.join(local_pb, mod)
            if os.path.exists(src_mod):
                shutil.copy2(src_mod, target_pb)
                
        print(Color.GREEN + "[+] Device Tree successfully deployed!" + Color.END)
        return True
    except Exception as e:
        print(Color.RED + f"[-] Error copying files: {e}" + Color.END)
        return False

def main():
    show_banner()
    
    # Set argument parses
    parser = argparse.ArgumentParser(description="High-Performance Automated Recovery Build Engine for Infinix GT 20 Pro (X6871)")
    parser.add_argument('-t', '--type', choices=['twrp', 'orangefox', 'pbrp'], default='twrp', help='Recovery compiler target type')
    parser.add_argument('-p', '--path', required=True, help='Absolute path to your minimal recovery AOSP manifest directory')
    parser.add_argument('-c', '--clean', action='store_true', help='Execute clean before compilation')
    parser.add_argument('-j', '--jobs', type=int, default=os.cpu_count(), help='Number of parallel compiler threads')
    parser.add_argument('-s', '--sync-sources', action='store_true', help='Execute repo sync to sync AOSP trees to latest releases')
    parser.add_argument('--dry-run', action='store_true', help='Deploy tree stubs and run verifier checks without compiling')
    
    args = parser.parse_args()
    
    is_windows = platform.system() == "Windows"
    manifest_dir = args.path.strip('\'"')
    
    # Resolve Windows paths to WSL paths if running on Windows
    if is_windows:
        print(Color.YELLOW + "[!] Windows platform detected. Commands will execute inside WSL." + Color.END)
        # Verify if directory exists on Windows first
        if not os.path.exists(manifest_dir):
            print(Color.RED + f"[-] Error: Directory '{manifest_dir}' not found on Windows host." + Color.END)
            sys.exit(1)
        wsl_manifest_dir = convert_win_path_to_wsl(manifest_dir)
        print(Color.GREEN + f"  [*] Windows Path: {manifest_dir} -> WSL Path: {wsl_manifest_dir}" + Color.END)
    else:
        if not os.path.exists(manifest_dir):
            print(Color.RED + f"[-] Error: Directory '{manifest_dir}' does not exist." + Color.END)
            sys.exit(1)
            
    # Verify that the directory contains the AOSP/TWRP build tree (build/envsetup.sh)
    envsetup_path = os.path.join(manifest_dir, "build", "envsetup.sh")
    if not os.path.exists(envsetup_path):
        print(Color.RED + f"[-] Error: '{manifest_dir}' is not a valid AOSP/TWRP build directory." + Color.END)
        print(Color.YELLOW + "    (Missing critical file: 'build/envsetup.sh')" + Color.END)
        print(Color.CYAN + "    Note: The --path parameter must point to a cloned minimal TWRP/OrangeFox manifest" + Color.END)
        print(Color.CYAN + "          workspace, not the generated device tree output folder." + Color.END)
        sys.exit(1)
            
    # Step 1: Deploy Device Tree files
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if not deploy_tree_sources(src_dir, manifest_dir, is_windows):
        print(Color.RED + "[-] Aborting build due to deployment failure." + Color.END)
        sys.exit(1)
        
    # Step 2: Formulate compiler commands
    build_steps = []
    
    # 2.1 Sync sources if requested
    if args.sync_sources:
        print(Color.BOLD + "\n[+] Adding latest sources sync commands (repo sync)..." + Color.END)
        build_steps.append("repo sync -c -j8 --force-sync --no-clone-bundle --no-tags")
        
    # 2.2 Clean workspace if requested
    if args.clean:
        print(Color.BOLD + "\n[+] Adding clean build command..." + Color.END)
        build_steps.append("source build/envsetup.sh && make clean")
        
    # 2.3 Set target definitions
    if args.type == 'twrp':
        target_product = "omni_X6871"
    elif args.type == 'orangefox':
        target_product = "omni_OrangeFox_X6871"
    else:
        target_product = "pb_X6871"
    
    # 2.4 Add compilation script sequence
    compilation_cmds = (
        "export ALLOW_MISSING_DEPENDENCIES=true && "
        "source build/envsetup.sh && "
        f"lunch {target_product}-userdebug && "
        f"mka vendorbootimage -j{args.jobs}"
    )
    build_steps.append(compilation_cmds)
    
    # Join commands
    full_command = " && ".join(build_steps)
    
    if args.dry_run:
        print(Color.GREEN + "\n[+] Dry run checks completed successfully. Build script formulated:" + Color.END)
        print(Color.CYAN + f"  {full_command}" + Color.END)
        sys.exit(0)
        
    # Step 3: Run Compilation
    print(Color.BOLD + f"\n[+] Starting Recovery Compilation: {args.type.upper()} ({target_product}) with {args.jobs} jobs..." + Color.END)
    
    success = False
    if is_windows:
        success = run_wsl_command(full_command, cwd=manifest_dir)
    else:
        success = run_native_command(full_command, cwd=manifest_dir)
        
    if not success:
        print(Color.RED + "\n[-] COMPILATION FAILED: Compiler returned non-zero exit code. Inspect output details above." + Color.END)
        sys.exit(1)
        
    # Step 4: Verify built outputs and copy to project root
    print(Color.BOLD + "\n[+] Searching for compiled recovery image outputs..." + Color.END)
    out_rel_path = os.path.join("out", "target", "product", "X6871", "vendor_boot.img")
    out_abs_path = os.path.join(manifest_dir, out_rel_path)
    
    if os.path.exists(out_abs_path):
        print(Color.GREEN + f"  [x] Compiled image discovered: {out_abs_path}" + Color.END)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        dest_filename = f"{args.type.upper()}-X6871-{timestamp}-UNOFFICIAL.img"
        dest_abs_path = os.path.join(src_dir, dest_filename)
        
        try:
            shutil.copy2(out_abs_path, dest_abs_path)
            print(Color.GREEN + f"\n[+] SUCCESS: Recovery binary compiled successfully!" + Color.END)
            print(Color.BOLD + f"  [*] Target Path: {dest_abs_path}" + Color.END)
            print(f"  [*] File Size: {os.path.getsize(dest_abs_path) / (1024*1024):.2f} MB")
            print(f"  [*] SHA256 Checksum: {calculate_checksum(dest_abs_path)}")
        except Exception as e:
            print(Color.RED + f"[-] Error copying built binary: {e}" + Color.END)
    else:
        print(Color.RED + f"[-] Error: Build succeeded but compilation output image '{out_rel_path}' is missing." + Color.END)
        sys.exit(1)

if __name__ == "__main__":
    main()
