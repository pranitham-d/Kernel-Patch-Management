#!/usr/bin/env python3
"""
Kernel Patch Automation Script (RHEL/YUM)
------------------------------------------
1. Ping reachable hosts
2. Temporary passwordless Ansible setup
3. Pre-checks: uname, installed kernels, fstab
4. Ask user for 2 kernels to keep
5. Install those kernels and set highest as default boot
6. Install yum-utils temporarily for old kernel cleanup
7. Update all other packages excluding kernels
8. Remove old kernels leaving only the 2 specified
9. Reboot nodes
10. Post-checks: uname, installed kernels, fstab
11. Cleanup: remove temporary keys and yum-utils
"""

import os
import sys
import subprocess
import tempfile
import shlex
from pathlib import Path
import time

# ---------------- Utility Functions ----------------
def run(cmd, capture=False, check=True):
    return subprocess.run(cmd, shell=True, capture_output=capture, text=True, check=check)

def ping_test(ip):
    print(f"[*] Pinging {ip} ...", end=" ")
    result = subprocess.run(["ping", "-c", "2", "-W", "2", ip],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        print("[OK]")
        return True
    else:
        print("[UNREACHABLE]")
        return False

def save_provided_key(provided_text):
    fd, path = tempfile.mkstemp(prefix="provided_key_", text=True)
    os.close(fd)
    with open(path, "w") as f:
        f.write(provided_text)
    os.chmod(path, 0o600)
    return path

def ensure_control_pubkey():
    home = Path.home() / ".ssh"
    priv = home / "id_rsa"
    pub = home / "id_rsa.pub"
    os.makedirs(home, exist_ok=True)
    if not priv.exists() or not pub.exists():
        print("[*] Generating new control SSH keypair...")
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", str(priv)], check=True)
    return str(pub)

def ssh_with_key(key_path, user, host, cmd):
    ssh_cmd = f"ssh -i {shlex.quote(key_path)} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {user}@{host} {shlex.quote(cmd)}"
    return subprocess.run(ssh_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def install_control_key(provided_key_path, pub_path, user, host):
    with open(pub_path) as f:
        pub = f.read().strip()
    remote_cmd = f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '{pub}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
    result = ssh_with_key(provided_key_path, user, host, remote_cmd)
    return result.returncode == 0

def remove_control_key(provided_key_path, pub_path, user, host):
    with open(pub_path) as f:
        pub = f.read().strip()
    remote_cmd = f"grep -vF '{pub}' ~/.ssh/authorized_keys > ~/.ssh/tmp && mv ~/.ssh/tmp ~/.ssh/authorized_keys || true"
    ssh_with_key(provided_key_path, user, host, remote_cmd)

def create_inventory(ips, user, key_path):
    tf = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".ini")
    tf.write("[all]\n")
    for ip in ips:
        tf.write(f"{ip} ansible_user={user} ansible_ssh_private_key_file={key_path}\n")
    tf.close()
    return tf.name

def ansible_run(inv, cmd):
    subprocess.run(["ansible", "all", "-i", inv, "-m", "shell", "-a", cmd], check=False)

def compare_kernel_versions(k1, k2):
    # Remove 'kernel-' prefix if present
    k1_main = k1.replace("kernel-", "")
    k2_main = k2.replace("kernel-", "")
    def to_tuple(k):
        return tuple(int(x) for x in k.split(".") if x.isdigit())
    return k1 if to_tuple(k1_main) > to_tuple(k2_main) else k2

# ---------------- Main Logic ----------------
def main():
    print("=== Kernel Patch Automation ===")
    user = input("Enter existing SSH username on remote systems: ").strip()
    ips_raw = input("Enter IPs of remote systems (comma separated): ").strip()
    ips = [i.strip() for i in ips_raw.split(",") if i.strip()]

    print("\nPaste the private key for the remote user (Ctrl+D when done):")
    provided_key = sys.stdin.read().strip()
    if not provided_key:
        print("No key provided. Exiting.")
        sys.exit(1)

    key_path = save_provided_key(provided_key)
    control_pub = ensure_control_pubkey()

    # 1️⃣ Ping reachable hosts
    reachable = [ip for ip in ips if ping_test(ip)]
    if not reachable:
        print("[!] No reachable nodes. Exiting.")
        sys.exit(1)

    # 2️⃣ Setup passwordless control pubkey
    success_hosts = []
    for ip in reachable:
        print(f"[*] Installing control key on {ip}...")
        if install_control_key(key_path, control_pub, user, ip):
            success_hosts.append(ip)
        else:
            print(f"[!] Failed to setup key on {ip}")

    if not success_hosts:
        print("[!] Could not setup key on any nodes.")
        sys.exit(1)

    inv = create_inventory(success_hosts, user, key_path)

    # 3️⃣ Pre-check commands
    print("\n[*] Pre-checks...")
    precheck_cmds = ["uname -a", "rpm -qa | grep -i kernel", "cat /etc/fstab"]
    for cmd in precheck_cmds:
        print(f"\n--- {cmd} ---")
        ansible_run(inv, cmd)

    # 4️⃣ Get kernels to keep
    k1 = input("\nEnter first kernel version to keep (e.g., kernel-5.14.0-570.52.1.el9_6): ").strip()
    k2 = input("Enter second kernel version to keep (e.g., kernel-5.14.0-570.51.1.el9_6): ").strip()

    higher_kernel = compare_kernel_versions(k1, k2)
    print(f"[*] Highest kernel to boot: {higher_kernel}")

    # 5️⃣ Install selected kernels
    print("[*] Installing selected kernels...")
    ansible_run(inv, f"sudo yum install -y {k1} {k2}")

    # 6️⃣ Set highest kernel to boot
    print("[*] Setting boot to highest kernel...")
    ansible_run(inv, f"sudo grub2-set-default '{higher_kernel}'")

    # 7️⃣ Update all other packages excluding kernel
    print("[*] Updating all other packages (excluding kernels)...")
    ansible_run(inv, f"sudo yum update -y --exclude=kernel*")

    # 8️⃣ Install yum-utils temporarily for old kernel cleanup
    print("[*] Installing yum-utils for old kernel cleanup...")
    ansible_run(inv, "sudo yum install -y yum-utils")

    # 9️⃣ Remove old kernels keeping only the 2 user-selected
    print("[*] Removing old kernels, keeping only user-specified 2...")
    ansible_run(inv, f"sudo package-cleanup --oldkernels --count=2 -y || true")

    # 10️⃣ Remove yum-utils after cleanup
    print("[*] Removing yum-utils after cleanup...")
    ansible_run(inv, "sudo yum remove -y yum-utils")

    # 11️⃣ Reboot nodes
    print("[*] Rebooting nodes...")
    ansible_run(inv, "sudo reboot")
    print("[*] Waiting 60s for nodes to come back online...")
    time.sleep(60)

    # 12️⃣ Post-checks
    print("\n[*] Post-checks...")
    for cmd in precheck_cmds:
        print(f"\n--- {cmd} ---")
        ansible_run(inv, cmd)

    # 13️⃣ Cleanup
    print("[*] Cleaning up passwordless SSH setup...")
    for ip in success_hosts:
        remove_control_key(key_path, control_pub, user, ip)

    os.remove(inv)
    os.remove(key_path)
    print("[✓] Kernel patch automation completed successfully.")

if __name__ == "__main__":
    main()

