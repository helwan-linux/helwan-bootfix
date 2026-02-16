import subprocess
import os
from pathlib import Path

class BootFixer:
    @staticmethod
    def run_fix() -> str:
        report = []
        
        # دالة مساعدة لتشغيل الأوامر بـ pkexec تلقائياً لو مش root
        def run_as_root(command):
            # نستخدم pkexec لفتح نافذة طلب كلمة السر الرسومية للمستخدم
            full_cmd = ["pkexec"] + command
            return subprocess.run(full_cmd, capture_output=True, text=True)

        try:
            # 1. فك حماية القرص
            report.append("--- [SYSTEM] Requesting Write Permissions ---")
            run_as_root(["mount", "-o", "remount,rw", "/"])
            
            # 2. تنفيذ mkinitcpio
            report.append("--- [PROCESS] Rebuilding Initramfs ---")
            proc1 = run_as_root(["mkinitcpio", "-P"])
            
            if proc1.stdout:
                report.append(proc1.stdout)
            
            if proc1.returncode != 0:
                report.append(f"✖ [FAILED] mkinitcpio failed (Code {proc1.returncode})")
                if proc1.stderr:
                    report.append(f"Details:\n{proc1.stderr}")
                return "\n".join(report)

            # 3. تنفيذ grub-mkconfig
            if Path("/usr/bin/grub-mkconfig").exists():
                report.append("\n--- [PROCESS] Updating GRUB Configuration ---")
                proc2 = run_as_root(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
                
                if proc2.stdout:
                    report.append(proc2.stdout)
                
                if proc2.returncode != 0:
                    report.append(f"✖ [FAILED] grub-mkconfig failed (Code {proc2.returncode})")
                    if proc2.stderr:
                        report.append(f"Details:\n{proc2.stderr}")
                    return "\n".join(report)

            report.append("\n✔ [SUCCESS] Boot fixed successfully for all users.")
            return "\n".join(report)
            
        except Exception as e:
            return f"✖ [ERROR] {str(e)}"
