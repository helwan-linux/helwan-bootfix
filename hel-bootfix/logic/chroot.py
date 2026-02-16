import subprocess
import os
from textwrap import dedent

class ChrootHelper:
    @staticmethod
    def chroot_script(root_partition: str) -> str:
        return dedent(f"""
            # Manual Instructions for Helwan Linux:
            sudo mount {root_partition} /mnt
            for i in /dev /dev/pts /proc /sys /run; do sudo mount --bind $i /mnt$i; done
            sudo chroot /mnt /bin/bash
        """)

    @staticmethod
    def execute_automated_chroot(root_partition: str):
        mount_point = "/mnt/helwan_repair"
        # المسارات المطلوب ربطها بالترتيب
        binds = ["dev", "dev/pts", "proc", "sys", "run"]
        
        try:
            if not os.path.exists(mount_point):
                os.makedirs(mount_point)
            
            # 1. Mount Root
            subprocess.run(["mount", "-o", "rw", root_partition, mount_point], check=True)
            
            # 2. Bind Systems
            for b in binds:
                target = os.path.join(mount_point, b)
                if not os.path.exists(target): os.makedirs(target)
                subprocess.run(["mount", "--bind", f"/{b}", target], check=True)

            # 3. Execute Repair
            repair_cmd = "mkinitcpio -P && grub-mkconfig -o /boot/grub/grub.cfg"
            result = subprocess.run(["chroot", mount_point, "/bin/bash", "-c", repair_cmd], 
                                     capture_output=True, text=True, check=True)
            
            status = f"✔ Repair Successful:\n{result.stdout}"

        except subprocess.CalledProcessError as e:
            status = f"✖ Critical Error: {e.stderr if e.stderr else str(e)}"
        except Exception as e:
            status = f"✖ Unexpected Error: {str(e)}"
        finally:
            # 4. Cleanup (فك الربط بالترتيب العكسي عشان مفيش حاجة تعلق)
            for b in reversed(binds):
                subprocess.run(["umount", "-l", os.path.join(mount_point, b)], stderr=subprocess.DEVNULL)
            subprocess.run(["umount", "-l", mount_point], stderr=subprocess.DEVNULL)
            
        return status
