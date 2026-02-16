#!/usr/bin/env python3

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QProcess

# ================== Paths ==================
if os.path.exists("/usr/share/helwan-bootfix"):
    BASE_DIR = "/usr/share/helwan-bootfix"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
# ===========================================

from logic.scanner import BootScanner
from logic.fixer import BootFixer
from logic.chroot import ChrootHelper
from logic.recovery import RecoveryManager
from logic.sysinfo import SystemInfoFetcher
from tabs.about import show_about_dialog

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(str(result))
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helwan BootFix")
        
        icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.resize(900, 650)
        self.threads = []
        
        self.live_process = QProcess(self)
        self.live_process.readyReadStandardOutput.connect(self.read_stdout)
        self.live_process.readyReadStandardError.connect(self.read_stderr)
        self.live_process.finished.connect(self.on_process_finished)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.setStyleSheet("""
            QTextEdit { 
                background-color: white; 
                color: black; 
                font-family: 'Monospace'; 
                font-size: 10pt;
            }
            QPushButton { padding: 8px; font-weight: bold; }
        """)

        self.init_tabs()
        self.init_menu_bar()

    def init_menu_bar(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(lambda: show_about_dialog(self))

    def init_tabs(self):
        self.init_tab_ui("System Scan", self.run_scan, "scan_output")
        self.init_tab_ui("Fix Boot", self.run_fix_live, "fix_output") 
        self.init_tab_ui("Chroot Helper", self.run_chroot, "chroot_output")
        self.init_tab_ui("Recovery Mode", self.run_recovery, "recovery_output")
        self.init_tab_ui("System Info", self.run_sysinfo, "sysinfo_output")
        self.init_log_tab()

    def init_tab_ui(self, title, func, output_name):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        output_widget = QTextEdit(readOnly=True)
        setattr(self, output_name, output_widget)
        btn = QPushButton(f"Execute {title}")
        btn.clicked.connect(func)
        layout.addWidget(btn)
        layout.addWidget(output_widget)
        self.tabs.addTab(tab, title)

    def init_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.log_output = QTextEdit(readOnly=True)
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Logs")
        save_btn = QPushButton("Save Log to File")
        clear_btn.clicked.connect(lambda: self.log_output.clear())
        save_btn.clicked.connect(self.save_logs_to_file)
        btn_layout.addWidget(clear_btn); btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout); layout.addWidget(self.log_output)
        self.tabs.addTab(tab, "Logs")

    def save_logs_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Text Files (*.txt)")
        if path:
            with open(path, "w") as f: f.write(self.log_output.toPlainText())
            QMessageBox.information(self, "Success", "Log saved successfully!")

    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        self.log_output.ensureCursorVisible()

    def read_stdout(self):
        data = self.live_process.readAllStandardOutput().data().decode()
        current_tab = self.tabs.currentIndex()
        if current_tab == 1: self.fix_output.insertPlainText(data); self.fix_output.ensureCursorVisible()
        elif current_tab == 3: self.recovery_output.insertPlainText(data); self.recovery_output.ensureCursorVisible()

    def read_stderr(self):
        data = self.live_process.readAllStandardError().data().decode()
        current_tab = self.tabs.currentIndex()
        if current_tab == 1: self.fix_output.insertPlainText(data); self.fix_output.ensureCursorVisible()
        elif current_tab == 3: self.recovery_output.insertPlainText(data); self.recovery_output.ensureCursorVisible()

    def run_fix_live(self):
        self.fix_output.clear()
        self.log_message("User initiated Live Boot Repair.")
        self.fix_output.append("--- [STARTING LIVE REPAIR] ---\n")
        cmd = "pkexec bash -c 'mount -o remount,rw /; mkinitcpio -P; grub-mkconfig -o /boot/grub/grub.cfg'"
        self.live_process.start("bash", ["-c", cmd])

    def on_process_finished(self):
        self.log_message("Background process finished.")
        current_tab = self.tabs.currentIndex()
        if current_tab == 1: self.fix_output.append("\n--- Done ---")
        elif current_tab == 3: self.recovery_output.append("\n--- Recovery Finished ---")

    def run_scan(self):
        self.scan_output.setPlainText("Scanning system details...")
        self.log_message("System Scan started.")
        th = WorkerThread(BootScanner.run_scan)
        th.finished.connect(lambda txt: self.scan_output.setPlainText(txt))
        th.start(); self.threads.append(th)

    def run_chroot(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Root Partition", "/dev")
        if path:
            self.log_message(f"Generating Chroot script for {path}")
            self.chroot_output.setPlainText(ChrootHelper.chroot_script(path))

    def run_recovery(self):
        self.recovery_output.clear()
        self.log_message("Starting Recovery Mode...")
        from logic.recovery import RecoveryManager
        cmd_chain = RecoveryManager.run()
        self.live_process.start("pkexec", ["bash", "-c", cmd_chain])

    def run_sysinfo(self):
        self.log_message("Fetching System Info.")
        self.sysinfo_output.setPlainText(SystemInfoFetcher.fetch())

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Noto Sans", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
