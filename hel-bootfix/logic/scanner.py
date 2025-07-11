from pathlib import Path
import subprocess

class BootScanner:
    @staticmethod
    def run_scan() -> str:
        try:
            report_lines = ["*** Helwan BootFix – Scan Report ***\n"]

            grub_cfg = Path("/boot/grub/grub.cfg")
            if grub_cfg.exists():
                report_lines.append("✔ GRUB config found: /boot/grub/grub.cfg")
            else:
                report_lines.append("✖ GRUB config NOT found!")

            boot_dir = Path("/boot")
            kernels = sorted(boot_dir.glob("vmlinuz-*"))
            ramdisks = sorted(boot_dir.glob("initramfs-*"))
            report_lines.append(f"Kernels detected: {len(kernels)}")
            report_lines.append(f"Initramfs images: {len(ramdisks)}")

            fstab = Path("/etc/fstab")
            if fstab.exists():
                report_lines.append("✔ fstab exists (/etc/fstab)")
            else:
                report_lines.append("✖ /etc/fstab missing!")

            lsblk_out = subprocess.check_output(["lsblk", "-f"], text=True)
            report_lines.append("\n--- lsblk -f ---\n" + lsblk_out)

            return "\n".join(report_lines)
        except Exception as e:
            return f"Error during scan: {e}"
