# tabs/about.py

from PyQt5.QtWidgets import QMessageBox

def show_about_dialog(parent):
    QMessageBox.information(
        parent,
        "About Helwan BootFix",
        "🛠️ Helwan BootFix\n\n"
        "Tool to scan and fix boot issues on Linux.\n"
        "Version: 0.3\n"
        "Author: Saeed Badrelden\n"
        
    )
