# 🚀 Grand Unified Master Toolbox v26.0
### A comprehensive Linux system administration toolkit

---

## Table of Contents

1. [What Is Toolbox?](#what-is-toolbox)
2. [Installation](#installation)
3. [How to Run It](#how-to-run-it)
4. [Platform Support](#platform-support)
5. [The Main Menu — At a Glance](#the-main-menu--at-a-glance)
6. [Section 1 — Maintenance](#section-1--maintenance)
   - [10 — Install Core Tools](#10--install-core-tools)
   - [11 — System Update](#11--system-update)
   - [12 — System Cleanup](#12--system-cleanup)
   - [13 — Kill Zombie Processes](#13--kill-zombie-processes)
   - [14 — Service Manager](#14--service-manager)
7. [Section 2 — Rescue & Recovery](#section-2--rescue--recovery)
   - [20 — Auto-Diagnostic Repair](#20--auto-diagnostic-repair)
   - [21 — Graphics Repair](#21--graphics-repair)
   - [22 — Disk Analyzer](#22--disk-analyzer)
   - [23 — GRUB Rescue Guide](#23--grub-rescue-guide)
   - [24 — Boot Repair](#24--boot-repair)
8. [Section 3 — Dev, AI & Containers](#section-3--dev-ai--containers)
   - [30 — Ollama AI Setup](#30--ollama-ai-setup)
   - [31 — Podman Manager](#31--podman-manager)
   - [32 — Install Go](#32--install-go)
   - [33 — User Management](#33--user-management)
   - [34 — Docker Manager](#34--docker-manager)
   - [35 — Update Ollama](#35--update-ollama)
9. [Section 4 — Hardware & Android](#section-4--hardware--android)
   - [40 — Android Manager](#40--android-manager)
   - [41 — GPU Monitor](#41--gpu-monitor)
   - [42 — Stress Test Suite](#42--stress-test-suite)
   - [43 — System Information](#43--system-information)
   - [44 — Network Tools](#44--network-tools)
10. [Section 5 — Backup & Restore](#section-5--backup--restore)
    - [50 — Backup Manager](#50--backup-manager)
11. [System Options](#system-options)
12. [CLI Quick-Fire Reference](#cli-quick-fire-reference)
13. [Behind the Scenes](#behind-the-scenes)
14. [Tips & Troubleshooting](#tips--troubleshooting)

---

## What Is Toolbox?

Toolbox is a single-file Bash script that bundles together the most common Linux administration tasks into one interactive menu-driven interface. Instead of hunting through man pages or remembering a dozen different command syntaxes, you navigate numbered menus and Toolbox runs the right commands for you.

It is designed to be **hardware-aware**. On startup it detects your GPU vendor (Nvidia, AMD, Intel Arc, or Intel iGPU), your CPU, your RAM, and your package manager (`apt`, `dnf`, or `pacman`). Every subsequent action — driver installation, GPU monitoring, package commands — adapts to what it finds.

---

## Installation

Run the script once from anywhere and it will offer to install itself system-wide:

```bash
bash toolbox.sh
```

When prompted, choose **yes**. It will:

- Copy itself to `/usr/local/bin/toolbox`
- Install core dependencies (`curl`, `wget`, `git`, `htop`, `ncdu`, `bc`, `pciutils`)
- Optionally install extras like `scrcpy`, `podman`, `stress-ng`, and `glmark2`

After that you can launch it from any terminal simply by typing:

```bash
toolbox
```

---

## How to Run It

Toolbox has two modes:

| Mode | How | When to use |
|---|---|---|
| **Interactive** | `toolbox` (no arguments) | Day-to-day use. Navigate menus with number keys. |
| **CLI one-shot** | `toolbox --flag` | Scripting, cron jobs, or when you know exactly what you need. |

Every interactive menu ends with **99. Back**, which returns you to the previous level. Confirmations (`y/n`) appear before anything destructive.

---

## Platform Support

| Component | Supported Options |
|---|---|
| **Package Manager** | `apt` (Debian/Ubuntu), `dnf` (Fedora/RHEL), `pacman` (Arch) |
| **GPU Vendor** | Nvidia, AMD, Intel Arc (DG2/Alchemist), Intel iGPU |
| **Architecture** | x86_64 (Linux-amd64) |

Toolbox detects these automatically. Some features (e.g., `ubuntu-drivers autoinstall`) are distribution-specific and will be skipped or substituted when they don't apply.

---

## The Main Menu — At a Glance

```
 ╔═══════════════════════════════╗  ╔═══════════════════════════════╗
 ║     1. MAINTENANCE            ║  ║     2. RESCUE & RECOVERY      ║
 ╚═══════════════════════════════╝  ╚═══════════════════════════════╝
  10. Install Core Tools             20. Auto-Diagnostic Repair
  11. System Update                  21. Graphics Repair
  12. System Cleanup                 22. Disk Analyzer
  13. Kill Zombie Processes          23. GRUB Rescue Guide
  14. Service Manager                24. Boot Repair

 ╔═══════════════════════════════╗  ╔═══════════════════════════════╗
 ║     3. DEV, AI & CONTAINERS   ║  ║     4. HARDWARE & ANDROID     ║
 ╚═══════════════════════════════╝  ╚═══════════════════════════════╝
  30. Ollama AI Setup                40. Android Manager (ADB)
  31. Podman Manager                 41. GPU Monitor
  32. Install Go (Latest)            42. Stress Test Suite
  33. User Management                43. System Information
  34. Docker Manager                 44. Network Tools
  35. Update Ollama

 ╔═══════════════════════════════╗
 ║     5. BACKUP & RESTORE       ║
 ╚═══════════════════════════════╝
  50. Backup Manager

  80. Reboot System  |  90. View Logs  |  99. Exit
```

---

## Section 1 — Maintenance

This section covers routine system housekeeping: keeping packages current, tidying up disk space, and managing background services.

---

### 10 — Install Core Tools

Installs a curated set of system utilities in one go:

`curl`, `wget`, `bc`, `htop`, `ncdu`, `timeshift`, `testdisk`, `git`, `mc`, `tree`, `vim`, `nano`, `rsync`

A confirmation prompt lists every package before anything is downloaded. This is the fastest way to get a fresh system ready for the other Toolbox features.

**CLI equivalent:** `toolbox --install-tools`

---

### 11 — System Update

Runs a full package refresh and upgrade using whichever package manager was detected.

| Step | What happens |
|---|---|
| 1 | Backs up `/etc/apt/sources.list` (on Debian systems) to `~/.toolbox/backups/` |
| 2 | Runs the package index update (`apt update` / `dnf check-update` / `pacman -Sy`) |
| 3 | Asks for confirmation before running the upgrade |

**CLI equivalent:** `toolbox --update`

---

### 12 — System Cleanup

Reclaims disk space from several common sources:

| Target | What it does |
|---|---|
| **Journal logs** | Trims systemd journal to the last 7 days |
| **Package cache** | Runs the package manager's built-in autoremove and clean |
| **/tmp files** | Deletes files in `/tmp` older than 7 days (after confirmation) |
| **Toolbox logs** | Removes its own log files older than 30 days (after confirmation) |

**CLI equivalent:** `toolbox --cleanup`

---

### 13 — Kill Zombie Processes

Scans for zombie processes (state `Z`) and displays them with their Parent PID (PPID).

You can then either:
- Type a specific **PPID** to kill just that parent process.
- Type `all` to kill every zombie's parent at once.

Zombie processes cannot be killed directly — killing the parent is the correct approach, which is exactly what this tool does.

**CLI equivalent:** `toolbox --kill-zombies`

---

### 14 — Service Manager

A sub-menu for controlling systemd services without memorising `systemctl` flags:

| Option | Action |
|---|---|
| 1 | List all currently running services |
| 2 | Start a named service |
| 3 | Stop a named service |
| 4 | Restart a named service |
| 5 | Enable a service (survives reboot) |
| 6 | Disable a service |

Each option prompts you for the service name (e.g., `nginx`, `sshd`, `ollama`).

> **No CLI equivalent** — this one is interactive only because it is a persistent sub-menu.

---

## Section 2 — Rescue & Recovery

These tools are designed for when things have gone wrong: broken packages, missing boot loaders, graphics driver failures, or a full disk.

---

### 20 — Auto-Diagnostic Repair

Runs a sequence of common fixes automatically:

| Step | What it does |
|---|---|
| **Package repair** | On `apt`: runs `dpkg --configure -a`, `apt --fix-broken install`, and `apt install -f`. On `dnf`: runs `dnf check` and `dnf distro-sync`. |
| **GRUB rebuild** | Backs up `/etc/default/grub`, then regenerates the GRUB configuration |
| **Filesystem check** | Optionally schedules an `fsck` on the next reboot by creating `/forcefsck` |

Good first step when the system is behaving erratically and you're not sure what's wrong.

**CLI equivalent:** `toolbox --auto-diag`

---

### 21 — Graphics Repair

A dedicated sub-menu for GPU driver problems. It displays the detected GPU vendor and model at the top so you always know what it's working with.

| Option | Action |
|---|---|
| 1 | **Auto-Install Drivers** — installs the correct driver stack for your detected GPU (see [GPU-Specific Details](#gpu-specific-details) below) |
| 2 | **Purge All Graphics Drivers** — removes every Nvidia, AMD, and FGLRX package. Backs up `xorg.conf` first. |
| 3 | **Reinstall Mesa/Xorg** — force-reinstalls the core X server and Mesa packages |
| 4 | **Check Driver Status** — shows `lspci -k` output for all display devices, plus vendor-specific info (`nvidia-smi`, `clinfo`, `vainfo`) |
| 5 | **Install Vulkan Support** — installs `vulkan-tools` and `mesa-vulkan-drivers` |
| 6 | **Intel Arc Specific Setup** — opens the dedicated Intel Arc sub-menu (see below) |

#### GPU-Specific Details

**Nvidia:** Uses `ubuntu-drivers autoinstall` on Ubuntu, or falls back to installing `nvidia-driver-535` / `akmod-nvidia`.

**AMD:** Installs `mesa-vulkan-drivers` and `xf86-video-amdgpu`.

**Intel Arc:** Adds the official Intel GPU repository, then installs the full Level Zero, OpenCL, VA-API, and Mesa stack. Also adds your user to the `render` group.

#### Intel Arc Sub-Menu (Option 6)

Intel Arc GPUs have more moving parts than most, so they get their own dedicated menu:

| Option | Action |
|---|---|
| 1 | Install the full driver stack (Level Zero, OpenCL, Mesa, VA-API) |
| 2 | Install Intel oneAPI Base Toolkit (needed for compute and AI workloads) |
| 3 | Test GPU access — checks `/dev/dri/` devices, user group membership, and runs `clinfo` and `vainfo` |
| 4 | Check GPU clocks & performance via `intel_gpu_top` |
| 5 | Install Intel GPU monitoring tools (`intel-gpu-tools`, `clinfo`, `vainfo`, `hwinfo`) |
| 6 | Configure environment variables for hardware media encoding (`LIBVA_DRIVER_NAME`, `LIBVA_DRIVERS_PATH`) |
| 7 | View GPU topology — PCI info, DRM devices, and hardware card details |
| 8 | Fix common issues — automatically applies three frequent fixes: adds user to `render`/`video` groups, adds the `i915.force_probe=*` kernel parameter to GRUB, and installs firmware packages |

---

### 22 — Disk Analyzer

Launches `ncdu` (installs it first if missing) — an interactive, terminal-based disk usage tool that lets you drill down into directories and see exactly what's eating your space.

Three scan scopes are offered:

| Option | Scans |
|---|---|
| 1 | The entire filesystem (`/`), excluding `/proc`, `/sys`, and `/dev` |
| 2 | Your home directory only |
| 3 | A custom path you type in |

**CLI equivalent:** `toolbox --disk-analyze`

---

### 23 — GRUB Rescue Guide

A printed cheat sheet — no commands are actually executed. Useful when you're booting into GRUB rescue mode from a separate terminal or phone and need the exact syntax at a glance.

It covers both the rescue-mode commands (`set root`, `insmod normal`, etc.) and the post-boot repair commands (`update-grub`, `grub-install`).

**CLI equivalent:** `toolbox --grub-cheatsheet`

---

### 24 — Boot Repair

Attempts to fix a system that won't boot by performing three steps in sequence:

1. **Reinstalls GRUB** to a device you specify (e.g., `/dev/sda`)
2. **Rebuilds the GRUB configuration** (`update-grub` or `grub2-mkconfig`)
3. **Regenerates initramfs** (`update-initramfs` on Debian, `dracut` on Fedora/RHEL)

A confirmation prompt appears before anything runs.

> **No CLI equivalent** — boot repair requires interactive input (the boot device path).

---

## Section 3 — Dev, AI & Containers

Tools for developers and anyone running local AI models or containerised services.

---

### 30 — Ollama AI Setup

Sets up and configures [Ollama](https://ollama.com) — a local LLM inference server — with full GPU integration.

**What it does, step by step:**

1. Checks if Ollama is installed. If not, downloads and runs the official installer.
2. Displays your detected GPU.
3. Runs a **GPU-specific configuration branch**:

| Your GPU | What happens |
|---|---|
| **Intel Arc** | Presents four options: install drivers only, configure Ollama only, do both, or skip. The configuration writes a systemd override that sets `OLLAMA_INTEL_GPU=1`, `ONEAPI_DEVICE_SELECTOR=level_zero:gpu`, and related environment variables. |
| **AMD (Polaris)** | Optionally applies a patch that sets `HSA_OVERRIDE_GFX_VERSION=8.0.3` for older RX 570/580 cards that need it. |
| **Nvidia** | Checks that `nvidia-smi` is present. If not, offers to run the Graphics Repair installer. Nvidia GPUs work with Ollama out of the box once drivers are installed. |

4. Enables and starts the `ollama` systemd service.
5. Optionally tests the connection by hitting the Ollama API endpoint.
6. Optionally downloads a model. For Intel Arc systems it recommends:
   - `llama3.2:3b` — fast, good for testing
   - `llama3.2:8b` — balanced performance
   - `mistral:7b` — general purpose
   - `codellama:7b` — coding tasks

**CLI equivalent:** `toolbox --ollama-setup`

---

### 31 — Podman Manager

A project-oriented interface for managing Podman containers and pods.

| Option | Action |
|---|---|
| 1 | Create a new project folder under `~/container_projects/` |
| 2 | Load an existing project folder |
| 3 | Create a named Pod |
| 4 | Run `podman-compose up -d` using the active project's `docker-compose.yml` or `compose.yml` |
| 5 | List all containers and pods |
| 6 | Stop a container by name or ID |
| 7 | Remove a container by name or ID |
| 8 | Follow the live logs of a container (opens in a new terminal window) |

The active project and pod are tracked across the menu session and displayed at the top.

> **No CLI equivalent** — this is a stateful interactive workflow.

---

### 32 — Install Go

Downloads and installs the latest Go toolchain from `go.dev`:

1. Fetches the latest version string from the Go download API.
2. Downloads the `.tar.gz` for `linux-amd64`.
3. Extracts to `/usr/local/go/`.
4. Appends `/usr/local/go/bin` and `$HOME/go/bin` to your `PATH` in `~/.bashrc` if not already present.

**CLI equivalent:** `toolbox --install-go`

---

### 33 — User Management

Handles common user account tasks:

| Option | Action |
|---|---|
| 1 | Add an existing user to the `sudo` (or `wheel` on RHEL) group |
| 2 | Create a new user, optionally adding them to sudo immediately |
| 3 | Delete a user and their home directory (with confirmation) |
| 4 | List all user accounts on the system |
| 5 | Change a user's password |

> **No CLI equivalent** — interactive prompts required.

---

### 34 — Docker Manager

Basic Docker lifecycle management for those who use Docker instead of (or alongside) Podman:

| Option | Action |
|---|---|
| 1 | Install Docker (enables and starts the service automatically) |
| 2 | Install Docker Compose (downloads the latest binary from GitHub) |
| 3 | List all containers (running and stopped) |
| 4 | Start a container by name or ID |
| 5 | Stop a container by name or ID |
| 6 | Follow live logs for a container (opens in a new terminal) |
| 7 | Add a user to the `docker` group (avoids needing `sudo` for every command) |

> **No CLI equivalent** — interactive prompts required.

---

### 35 — Update Ollama

Checks for and applies updates to an already-installed Ollama:

1. Reads the currently installed version via `ollama version`.
2. Queries the GitHub releases API to find the latest tagged version.
3. Compares the two. If they match, reports that Ollama is already up to date.
4. If an update is available, stops the service, runs the official installer, restarts the service, and then verifies the new version and service health.
5. Falls back to re-running the installer directly if the GitHub API is unreachable.

**CLI equivalent:** `toolbox --ollama-update`

---

## Section 4 — Hardware & Android

Monitoring, benchmarking, device management, and networking.

---

### 40 — Android Manager

Controls an Android device over ADB (Android Debug Bridge) and Scrcpy. Connected devices are listed at the top of the menu each time it redraws.

| Option | Action |
|---|---|
| 1 | Connect to a device wirelessly by IP (assumes port 5555) |
| 2 | Install an APK from a local file path |
| 3 | Push a file from your PC to the device (default destination: `/sdcard/Download/`) |
| 4 | Pull a file from the device to your PC |
| 5 | Stream live Android logcat output (opens in a new terminal) |
| 6 | Launch Scrcpy screen mirror with options: Normal Quality, High Quality (8 Mbps), Screen Recording, or Wireless TCP/IP mode |
| 7 | Open an interactive ADB shell (opens in a new terminal) |
| 8 | Reboot the device — Normal, into Recovery, or into the Bootloader |

**CLI equivalent:** `toolbox --android`

---

### 41 — GPU Monitor

Launches a live, continuously refreshing GPU monitor appropriate for your hardware:

| GPU Vendor | Tool Used |
|---|---|
| Nvidia | `nvidia-smi` (refreshes every 1 second via `watch`) |
| AMD / Intel | `radeontop` (installed automatically if missing) |

The monitor opens in a new terminal window so it doesn't block the main menu.

**CLI equivalent:** `toolbox --gpu-monitor`

---

### 42 — Stress Test Suite

Pushes your hardware to its limits for thermal and stability testing. A warning is displayed before the menu loads.

| Option | What it stresses | Default duration |
|---|---|---|
| 1 | **CPU** — uses `stress-ng` with one worker per core | 60 seconds |
| 2 | **GPU** — runs `glmark2` fullscreen benchmark | Until benchmark completes |
| 3 | **Memory** — allocates up to 80% of RAM across 2 VM workers | 60 seconds |
| 4 | **Combined** — CPU + Memory + 4 I/O workers simultaneously | 300 seconds |
| 5 | **Temperature Monitor** — runs `sensors` refreshing every 2 seconds (installs `lm-sensors` if needed) | Continuous until closed |

All duration-based tests let you override the default before they start.

**CLI equivalent:** `toolbox --stress-test`

---

### 43 — System Information

Prints a full system snapshot to the terminal, organised into sections:

| Section | What's shown |
|---|---|
| **System** | Hostname, OS, kernel version, uptime |
| **CPU** | Model name, core count, architecture |
| **Memory** | Full `free -h` output |
| **GPU** | Detected vendor plus `lspci` display device lines |
| **Storage** | All mounted `/dev` partitions with sizes and usage |
| **Network** | All non-loopback interfaces with their addresses |

**CLI equivalent:** `toolbox --system-info`

---

### 44 — Network Tools

A sub-menu of common networking tasks:

| Option | Action |
|---|---|
| 1 | **Network Configuration** — prints `ip addr show` and the default gateway |
| 2 | **Ping Test** — pings a host 4 times |
| 3 | **Port Scanner** — runs `nmap -sV` against a target (installs `nmap` if missing) |
| 4 | **Speedtest** — runs `speedtest-cli` (installed via pip if missing) |
| 5 | **Network Monitor** — launches `iftop` in a new terminal for live bandwidth monitoring |
| 6 | **DNS Lookup** — queries A, MX, and NS records for a domain using `dig` |

**CLI equivalent:** `toolbox --network`

---

## Section 5 — Backup & Restore

---

### 50 — Backup Manager

All backup operations store files in `~/.toolbox/backups/` by default, with timestamps in every filename so nothing ever overwrites anything.

| Option | Action |
|---|---|
| 1 | **Backup Home Directory** — creates a `.tar.gz` of `$HOME`, excluding `.cache` and Trash. You can specify a different destination directory. |
| 2 | **Backup System Configuration** — archives the entire `/etc` directory. Requires root. |
| 3 | **Full System Backup (Timeshift)** — creates a Timeshift snapshot with a timestamped comment. Installs Timeshift first if it's not present. |
| 4 | **List Backups** — shows both Toolbox backups and any Timeshift snapshots |
| 5 | **Restore from Backup** — extracts a previously created `.tar.gz` backup to a path you specify (default: `/`) |
| 6 | **Backup Installed Packages List** — saves the current package list to a text file. Format depends on your package manager (`dpkg --get-selections` / `rpm -qa` / `pacman -Qqe`). Useful for reinstalling an identical set of packages on a new system. |

**CLI equivalents:**

| Flag | Equivalent to |
|---|---|
| `toolbox --backup-home` | Option 1 (uses default destination) |
| `toolbox --backup-etc` | Option 2 |
| `toolbox --backup-packages` | Option 6 |

---

## System Options

These live at the bottom of the main menu and are available at any time:

| Option | Action |
|---|---|
| **80** | Reboot the system (confirmation prompt first) |
| **90** | View the current session's log file (last 50 lines) |
| **99** | Exit Toolbox |

---

## CLI Quick-Fire Reference

Every flag runs its task and exits immediately — no menus, no header, no `fastfetch`. Perfect for scripts and cron jobs.

```
─── Maintenance ─────────────────────────────────────────
  --install-deps        Install all dependencies
  --install-tools       Install core system tools
  --update              Update system packages
  --cleanup             Clean system (logs, cache, temp)
  --kill-zombies        Kill zombie processes

─── Rescue & Recovery ───────────────────────────────────
  --auto-diag           Run auto-diagnostic & repair
  --grub-cheatsheet     Print GRUB rescue command reference
  --disk-analyze        Launch interactive disk analyzer

─── Dev, AI & Containers ────────────────────────────────
  --ollama-setup        Configure Ollama & GPU integration
  --ollama-update       Update Ollama to latest version
  --install-go          Install latest Go toolchain

─── Hardware & Android ──────────────────────────────────
  --gpu-info            Display GPU information
  --gpu-monitor         Launch live GPU monitor
  --stress-test         Launch stress test suite
  --android             Launch Android device manager
  --network             Launch network tools
  --system-info         Display full system information

─── Backup & Restore ────────────────────────────────────
  --backup-home         Backup home directory
  --backup-etc          Backup system configuration (/etc)
  --backup-packages     Save installed package list

─── General ─────────────────────────────────────────────
  --version             Print version and exit
  --help                Print this reference and exit
```

### Example usage in a cron job

```bash
# Back up /etc every Sunday at 2 AM
0 2 * * 0 /usr/local/bin/toolbox --backup-etc

# Run a cleanup every night at 3 AM
0 3 * * * /usr/local/bin/toolbox --cleanup
```

---

## Behind the Scenes

Understanding how Toolbox works internally helps when reading the source or extending it.

### Startup Sequence

Every time Toolbox runs (interactive or CLI), it executes this sequence before doing anything else:

1. **`detect_package_manager`** — probes for `apt`, `dnf`, or `pacman` and sets the `INSTALL_CMD`, `UPDATE_CMD`, `UPGRADE_CMD`, and `CLEAN_CMD` variables accordingly. All package operations in the rest of the script use these variables, so the same code works on Debian, Fedora, and Arch.

2. **`detect_hardware`** — runs `lspci` to identify the GPU vendor and model, `lscpu` for the CPU, and `free` for total RAM. These values are stored in global variables (`GPU_VENDOR`, `GPU_MODEL`, `CPU_MODEL`, `CPU_CORES`, `TOTAL_RAM`) and used throughout.

3. **Header rendering** — if `fastfetch` is installed it runs a compact system info bar. Otherwise it prints a simple hostname/kernel line. A bordered box below it shows the Toolbox version, detected GPU, package manager, and local IP.

### Logging

Every action is logged to `~/.toolbox/logs/toolbox_YYYYMMDD_HHMMSS.log`. The log file is named with the timestamp of when the session started, so each run gets its own file. The **90** menu option lets you view the tail of the current session's log without opening a file manager.

### Backups Before Changes

Before modifying any system file, Toolbox calls `create_backup` to copy the original into `~/.toolbox/backups/` with a timestamp suffix. This applies to files like `/etc/default/grub`, `/etc/apt/sources.list`, and `/etc/X11/xorg.conf`.

### Terminal Spawning

Several features (live logs, GPU monitors, network monitors) need to run in a persistent terminal that doesn't block the main menu. Toolbox tries terminal emulators in this order:

1. `xterm`
2. `gnome-terminal`
3. `konsole`
4. `xfce4-terminal`

If none are available (or if there's no `$DISPLAY` — e.g., you're on an SSH session without X forwarding), it falls back to running the command inline in the current terminal.

---

## Tips & Troubleshooting

**"Permission denied" on package installs**
Most install and repair commands need root. Toolbox prepends `sudo` automatically, but your user must be in the `sudo` or `wheel` group. If you just created your account, use option **33 → 1** to add it.

**Intel Arc GPU not detected**
Intel Arc cards sometimes need the `i915.force_probe=*` kernel parameter to be visible to the driver. Go to **21 → 6 → 8** and let Toolbox add it to your GRUB configuration. A reboot is required afterward.

**Ollama says "no GPU found" after setup**
The most common cause is a missing group membership. After Toolbox adds you to the `render` group, you need to **log out and back in** (or start a new login shell with `newgrp render`) for the change to take effect. Then restart Ollama with `sudo systemctl restart ollama`.

**Zombie processes won't die**
Zombies are already dead — they're just waiting for their parent to call `wait()`. Killing the parent (what option **13** does) is the only way to reap them. If they reappear immediately, the parent is likely respawning them; check what that parent process is and whether it's a service you can restart or disable.

**"Could not fetch latest version" on Go or Ollama updates**
Both of these features reach out to external APIs (go.dev and api.github.com). If you're behind a corporate firewall or offline, they'll fail gracefully and tell you. The Ollama updater has a fallback path that skips the version check and just re-runs the installer directly.

**Disk Analyzer is slow on large drives**
`ncdu` has to walk the entire directory tree. On a large root partition this can take a minute or two. Scanning just `$HOME` (option 2) is much faster for everyday use.
