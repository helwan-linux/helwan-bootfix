# logic/scanner.py
from pathlib import Path
import subprocess

class BootScanner:
    @staticmethod
    def run_scan() -> str:
        try:
            report_lines = ["*** Helwan BootFix – Comprehensive Scan Report ***\n"]

            # 1. Boot Configuration Check
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

            # 2. Detailed Storage Info (Hard Drives, Partitions, Sizes)
            report_lines.append("\n--- Block Devices & Storage (lsblk) ---")
            # NAME: الاسم، TYPE: هارد ولا بارتيشن، SIZE: المساحة، FSUSED: المستخدم، FSUSE%: النسبة، MOUNTPOINT: نقطة الدمج، MODEL: موديل الهارد
            lsblk_out = subprocess.check_output(
                ["lsblk", "-o", "NAME,TYPE,SIZE,FSTYPE,FSUSED,FSUSE%,MOUNTPOINT,MODEL"], 
                text=True
            )
            report_lines.append(lsblk_out)

            # 3. ZRAM & Swap Analysis
            report_lines.append("\n--- Memory & ZRAM Status ---")
            try:
                zram_out = subprocess.check_output(["zramctl"], text=True)
                if zram_out:
                    report_lines.append("zram Configuration:\n" + zram_out)
                else:
                    report_lines.append("No active zram devices found.")
            except:
                report_lines.append("zramctl tool not available.")

            report_lines.append("\nActive Swaps (swapon):")
            try:
                swap_out = subprocess.check_output(["swapon", "--show"], text=True)
                if swap_out:
                    report_lines.append(swap_out)
                else:
                    report_lines.append("No active swap found.")
            except:
                report_lines.append("swapon command failed.")

            # 4. Partition Usage Detail (df)
            report_lines.append("\n--- Partition Mounts & Free Space (df -h) ---")
            df_out = subprocess.check_output(["df", "-h", "-x", "tmpfs", "-x", "devtmpfs"], text=True)
            report_lines.append(df_out)

            return "\n".join(report_lines)
            
        except Exception as e:
            return f"✖ Error during comprehensive scan: {str(e)}"
