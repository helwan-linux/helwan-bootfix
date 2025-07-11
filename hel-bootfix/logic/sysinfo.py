# logic/sysinfo.py

import platform
import socket
import psutil
import distro
import subprocess

class SystemInfoFetcher:
    @staticmethod
    def fetch():
        info = []

        info.append("📦 Distribution: " + distro.name(pretty=True))
        info.append("🧠 Architecture: " + platform.machine())
        info.append("🖥️ Hostname: " + socket.gethostname())
        info.append("🧮 Kernel: " + platform.release())

        mem = psutil.virtual_memory()
        info.append(f"💾 RAM: {round(mem.total / (1024**3), 2)} GB")

        info.append("⚙️ CPU: " + platform.processor())

        info.append("👤 User: " + psutil.users()[0].name)
        info.append("🌐 Online: " + ("Yes" if SystemInfoFetcher.check_online() else "No"))

        uptime_sec = int(psutil.boot_time())
        info.append("⏳ Boot Time (Epoch): " + str(uptime_sec))

        return "\n".join(info)

    @staticmethod
    def check_online():
        try:
            subprocess.check_call(["ping", "-c", "1", "1.1.1.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False
