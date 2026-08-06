import platform
import psutil
import subprocess
import sys

def get_gpu_info():
    """Detect GPU information without requiring extra dependencies.

    Tries nvidia-smi first (bundled with NVIDIA drivers), then PyTorch
    if it is already loaded in the process. Falls back gracefully if no
    GPU is found.
    """
    gpu_info = []

    # Method 1: NVIDIA GPUs via nvidia-smi (no extra dependencies needed)
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu_num = 0
            for line in result.stdout.strip().splitlines():
                if "," not in line:
                    continue
                gpu_num += 1
                name, vram = (part.strip() for part in line.split(","))
                gpu_info.append(f"GPU {gpu_num} = {name} ({vram} MB VRAM)")
    except (FileNotFoundError, subprocess.SubprocessError, OSError, ValueError):
        pass
    if not gpu_info:
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    vram_gb = torch.cuda.get_device_properties(i).total_memory // (1024 ** 3)
                    gpu_info.append(f"GPU {i + 1} = {torch.cuda.get_device_name(i)} ({vram_gb} GB VRAM)")
        except Exception:
            pass

    if not gpu_info:
        gpu_info.append("GPU = None detected")

    return gpu_info

def get_os_name():
    """Return a user-friendly, exact OS name that works on any platform."""
    system = platform.system()

    if system == "Linux":
        distro = _linux_distro_name()
        return distro if distro else "Linux"

    if system == "Darwin":
        version = platform.mac_ver()[0]
        return f"macOS {version}" if version else "iOS"

    if system == "Windows":
        try:
            version = platform.win32_ver()[0]
            parts = version.split(".") if version else []
            major = parts[0] if parts else ""
            minor = parts[1] if len(parts) > 1 else ""
            build = parts[-1] if parts else ""
            if major == "10" and build.isdigit():
                name = "Windows 11" if int(build) >= 22000 else "Windows 10"
                return f"{name} (build {build})"
            if major == "6":
                names = {"3": "Windows 8.1", "2": "Windows 8",
                         "1": "Windows 7", "0": "Windows Vista"}
                if minor in names:
                    return names[minor]
            if major == "5":
                return "Windows XP" if minor not in ("", "0") else "Windows 2000"
            return f"Windows {version}".strip()
        except Exception:
            pass
        return "Windows"

    if system == "SunOS":
        return "Solaris"
    version = platform.release()
    if not system:
        return version or "Unknown"
    return f"{system} {version}".strip() if version else system


def _parse_key_value_file(path):
    """Parse a simple KEY=VALUE file (e.g. os-release) into a dict.

    Returns None if the file cannot be read.
    """
    try:
        info = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                info[key] = value.strip().strip('"').strip("'")
        return info
    except OSError:
        return None


def _linux_distro_name():
    """Return the exact Linux distro name, or '' if it cannot be detected."""
    # Modern distros: /etc/os-release
    info = _parse_key_value_file("/etc/os-release")
    if info:
        pretty_name = info.get("PRETTY_NAME")
        if pretty_name:
            return pretty_name
        name = info.get("NAME")
        version = info.get("VERSION_ID")
        if name:
            return f"{name} {version}".strip()

    # Legacy distros: /etc/lsb-release
    info = _parse_key_value_file("/etc/lsb-release")
    if info:
        description = info.get("DISTRIB_DESCRIPTION")
        if description:
            return description
        dist_id = info.get("DISTRIB_ID")
        release = info.get("DISTRIB_RELEASE")
        if dist_id:
            return f"{dist_id} {release}".strip()

    # Legacy Red Hat family: /etc/redhat-release contains the full name
    try:
        with open("/etc/redhat-release", "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                return line
    except OSError:
        pass

    # Legacy Debian: /etc/debian_version contains just the version number
    try:
        with open("/etc/debian_version", "r", encoding="utf-8") as f:
            version = f.readline().strip()
            if version:
                return f"Debian {version}"
    except OSError:
        pass

    return ""

def collect():
    import platform
    import psutil
    
    user_os = get_os_name()  # Exact OS name (e.g. 'Ubuntu 24.04 LTS')
    
    release = str(platform.release())
    cpu_count = str(psutil.cpu_count(logical=True))
    processor = str(platform.processor())
    memory = str(psutil.virtual_memory().total // (1024 ** 3))  # Convert bytes to GB
    
    report = {
            "A User",
            f"OS = {user_os}",
            f"Platform Release = {release}",
            f"CPU Counts = {cpu_count}",
            f"Processor = {processor}",
            f"Total PC memory = {memory}GB",
        }
    
    report.update(get_gpu_info())
    
    return report

def collect_telemetry():
    try:
        telemetry = str(collect())
        
        with open("report.telemetry", "a") as f:
            f.write(telemetry + "\n")
            print(f"Data logged successfully to report.telemetry")
    except Exception as e:
        print(f"An error occurred while collecting telemetry: {e}")

