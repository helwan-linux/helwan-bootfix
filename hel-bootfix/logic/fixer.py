import subprocess
from pathlib import Path

class BootFixer:
    @staticmethod
    def run_fix() -> str:
        steps = []
        try:
            steps.append("Running: mkinitcpio -P")
            subprocess.run(["sudo", "mkinitcpio", "-P"], check=True)

            if Path("/usr/bin/grub-mkconfig").exists():
                steps.append("Running: grub-mkconfig -o /boot/grub/grub.cfg")
                subprocess.run([
                    "sudo", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"
                ], check=True)

            steps.append("✔ Boot repair commands executed successfully. Reboot and test.")
            return "\n".join(steps)
        except subprocess.CalledProcessError as e:
            steps.append(f"✖ Command failed: {e}")
            return "\n".join(steps)
        except Exception as e:
            return f"Unexpected error: {e}"
