# 🧠 Kernel Patch Automation Script (RHEL/YUM)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Ansible](https://img.shields.io/badge/Ansible-Automation-red?logo=ansible)
![RHEL](https://img.shields.io/badge/RHEL-Compatible-important?logo=redhat)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)

---

## 🚀 Overview

The **Kernel Patch Automation Script** is an **end-to-end Linux kernel patch management tool** built for **RHEL-based systems** using **Python + Ansible**.  
It automates kernel updates, cleanup, and reboots across multiple servers — ensuring **security**, **consistency**, and **zero manual intervention**.

🧩 **Ideal for:** DevOps Engineers, Linux Administrators, and Infrastructure Teams managing large-scale RHEL environments.

📦 Repository: [Patch-Management](https://github.com/pranitham-d/Kernel-Patch-Management)

---

## ✨ Features

| ✅ Capability | 🔍 Description |
|---------------|----------------|
| 🖥️ **Multi-Host Patching** | Patch kernels on multiple RHEL nodes simultaneously. |
| 🔑 **Temporary SSH Setup** | Creates & removes passwordless SSH keys securely. |
| 📋 **Pre/Post Checks** | Captures `uname`, `fstab`, and installed kernel versions. |
| ⚙️ **Kernel Retention** | Keep exactly two kernel versions for rollback assurance. |
| 🧹 **Automated Cleanup** | Installs and removes `yum-utils` dynamically. |
| 🔁 **Reboot Automation** | Reboots and verifies systems after patching. |
| 🧾 **Dynamic Inventory** | Generates & deletes a temporary Ansible inventory. |
| 🔒 **Security First** | No permanent keys or inventory files remain post-run. |

---

## 🏗️ Workflow Summary

| Step | Description |
|------|--------------|
| 1️⃣ | Ping reachable hosts |
| 2️⃣ | Setup temporary SSH key for automation |
| 3️⃣ | Run pre-checks (uname, kernel list, fstab) |
| 4️⃣ | Prompt for 2 kernels to retain |
| 5️⃣ | Install both kernels and set default boot to the higher version |
| 6️⃣ | Update all other packages (excluding kernels) |
| 7️⃣ | Install `yum-utils` temporarily |
| 8️⃣ | Remove old kernels (keep only 2) |
| 9️⃣ | Uninstall `yum-utils` |
| 🔟 | Reboot all nodes |
| 11️⃣ | Run post-checks |
| 12️⃣ | Clean up SSH and inventory files |

---

## ⚙️ Installation & Usage

### 🔹 1. Clone the Repository
```bash
git clone https://github.com/pranitham-d/Kernel-Patch-Management.git
cd Kernel-Patch-Management
```

### 🔹 2. Make the Script Executable
```bash
chmod +x kernel_patch_automation.py
```

### 🔹 3. Run the Script
```bash
./kernel_patch_automation.py
```

---

## 🧾 Input Prompts Explained

| Prompt | Description |
|--------|-------------|
| `Enter existing SSH username on remote systems:` | Username with `sudo` access on all target nodes. |
| `Enter IPs of remote systems (comma separated):` | List of hosts separated by commas. |
| `Paste the private key for the remote user:` | Paste private key (press **Ctrl+D** when done). |
| `Enter first kernel version to keep:` | e.g. `kernel-5.14.0-570.52.1.el9_6` |
| `Enter second kernel version to keep:` | e.g. `kernel-5.14.0-570.51.1.el9_6` |

---

## 🔐 Security Highlights

🔸 **Ephemeral SSH Authentication**
- Control node generates its own SSH keypair if not already present.  
- Temporarily adds it to `authorized_keys` on remote hosts.  
- Automatically removes entries after patching.

🔸 **No Residual Files**
- Temporary keys and inventory files are securely deleted post-execution.  
- Ensures no credential exposure or leftover access.

---

## 💡 Example Execution

```bash
=== Kernel Patch Automation ===
Enter existing SSH username on remote systems: automation
Enter IPs of remote systems (comma separated): 192.168.0.101,192.168.0.102
Paste the private key for the remote user (Ctrl+D when done):

[*] Pinging 192.168.0.101 ... [OK]
[*] Installing control key on 192.168.0.101...
[*] Pre-checks...
--- uname -a ---
Linux node1 5.14.0-362.8.1.el9_3.x86_64 ...

Enter first kernel version to keep: kernel-5.14.0-570.52.1.el9_6
Enter second kernel version to keep: kernel-5.14.0-570.51.1.el9_6
[*] Installing selected kernels...
[*] Removing old kernels, keeping only user-specified 2...
[*] Rebooting nodes...
[✓] Kernel patch automation completed successfully.
```

---

## 🌟 Advantages

### 🧩 **Operational Advantages**
- Fully hands-free multi-server patching.
- No permanent inventory or SSH setup.
- Ensures rollback capability with two kernel retention.
- Parallel patching using Ansible for high speed.

### 🔒 **Security Advantages**
- Temporary and isolated access via SSH key injection.
- Automatic cleanup prevents persistent access.
- Secure file handling (chmod 600, auto-delete).

### ⚡ **Efficiency Advantages**
- Reduces maintenance windows drastically.
- Avoids manual YUM and GRUB operations.
- Consistent results across all nodes.

---

## 🧰 Technical Stack

| Component | Technology |
|------------|-------------|
| **Language** | Python 3 |
| **Automation Engine** | Ansible |
| **Compatible OS** | RHEL / CentOS / Rocky / AlmaLinux |
| **Package Manager** | YUM / DNF |
| **Utilities Used** | SSH, GRUB2, yum-utils |

---

## 🧠 Troubleshooting

| Problem | Likely Cause | Solution |
|----------|---------------|----------|
| `sudo: package-cleanup: command not found` | `yum-utils` missing | The script auto-installs and removes it. |
| `UNREACHABLE` during ping | Network/firewall issue | Ensure ICMP and SSH are allowed. |
| SSH access denied | Incorrect key or username | Verify user and re-enter private key. |

---

## 📸 Architecture Diagram (Conceptual)

```
+---------------------------+
| Control Node (Python+Ansible)
|   - Generates temp SSH key
|   - Creates dynamic inventory
|   - Runs patch automation
+---------------------------+
           │
           ▼
+---------------------------------------+
| Multiple Target Nodes (RHEL)
|   - Receives temporary SSH key
|   - Executes prechecks & patching
|   - Reboots & validates kernel
|   - Removes temporary access
+---------------------------------------+
```

---

## 🧑‍💻 Author

**👤 Pranitham Devarakonda**  
🖥️ *Linux Automation & Infrastructure Engineer*  
💬 “Everything about Linux automation excites me — this project embodies that passion.”  

🌐 [LinkedIn](https://www.linkedin.com/in/) • 🐙 [GitHub](https://github.com/pranitham-d)  

---

## 🪪 License

This project is licensed under the **MIT License**.  
You’re free to use, modify, and distribute it — just give credit where it’s due.  

---

⭐ **If you find this project helpful, consider giving it a star on GitHub!** ⭐
