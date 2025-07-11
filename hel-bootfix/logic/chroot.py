from textwrap import dedent

class ChrootHelper:
    @staticmethod
    def chroot_script(root_partition: str) -> str:
        return dedent(
            f"""
            # Mount root partition
            mount {root_partition} /mnt

            # Bind system dirs
            mount --types proc /proc /mnt/proc
            mount --rbind /sys  /mnt/sys
            mount --rbind /dev  /mnt/dev
            mount --make-rslave /mnt/sys
            mount --make-rslave /mnt/dev

            # Chroot
            chroot /mnt /bin/bash

            # Inside chroot, you can run:
            mkinitcpio -P
            grub-mkconfig -o /boot/grub/grub.cfg
            exit
            umount -R /mnt
            reboot
            """
        )
