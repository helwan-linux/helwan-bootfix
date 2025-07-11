# logic/recovery.py

import subprocess

class RecoveryManager:
    @staticmethod
    def run():
        output = []

        try:
            output.append("✔ Running mkinitcpio...")
            subprocess.run(["sudo", "mkinitcpio", "-P"], check=True)
            output.append("✔ Initramfs rebuilt")

            output.append("✔ Generating GRUB config...")
            subprocess.run(["sudo", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"], check=True)
            output.append("✔ GRUB config generated")

            output.append("✔ Boot entries updated")

        except subprocess.CalledProcessError as e:
            output.append("✖ Error during recovery: " + str(e))

        return "\n".join(output)

