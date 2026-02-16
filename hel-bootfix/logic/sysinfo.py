import platform, socket, psutil, distro, subprocess

class SystemInfoFetcher:
    @staticmethod
    def fetch():
        info = [
            f"📦 Distro: {distro.name(pretty=True)}",
            f"🧠 Arch: {platform.machine()}",
            f"🖥️ Host: {socket.gethostname()}",
            f"🧮 Kernel: {platform.release()}"
        ]
        
        users = psutil.users()
        current_user = users[0].name if users else "LiveUser/Root"
        info.append(f"👤 User: {current_user}")
        
        mem = psutil.virtual_memory()
        info.append(f"💾 RAM: {round(mem.total / (1024**3), 2)} GB")
        return "\n".join(info)
