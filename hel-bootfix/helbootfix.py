#!/usr/bin/env python3

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QThread, pyqtSignal

# ================== دعم التشغيل من التثبيت أو من المصدر ==================
if os.path.exists("/usr/share/helwan-bootfix"):
    BASE_DIR = "/usr/share/helwan-bootfix"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)
# ==========================================================================

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
        result = self.func(*self.args, **self.kwargs)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    COLOR_MAP = {"✔": "#2ecc71", "✖": "#e74c3c", "⚠": "#f1c40f"}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helwan BootFix")
        icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(900, 650)

        self.threads = []
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.status = self.statusBar()
        self.set_status("Ready.")

        self.init_tabs()
        self.init_menu_bar()

    def init_menu_bar(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(lambda: show_about_dialog(self))

    def init_tabs(self):
        self.init_scan_tab()
        self.init_fix_tab()
        self.init_chroot_tab()
        self.init_recovery_tab()
        self.init_sysinfo_tab()
        self.init_log_tab()

    def init_scan_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.scan_output = QTextEdit(readOnly=True)
        btn = QPushButton("Run System Scan")
        btn.clicked.connect(self.run_scan)
        layout.addWidget(btn)
        layout.addWidget(self.scan_output)
        self.tabs.addTab(tab, "System Scan")

    def init_fix_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.fix_output = QTextEdit(readOnly=True)
        btn = QPushButton("Attempt Auto Fix (Root)")
        btn.clicked.connect(self.run_fix)
        layout.addWidget(btn)
        layout.addWidget(self.fix_output)

        bar = QHBoxLayout()
        copy_btn = QPushButton("Copy Report")
        copy_btn.clicked.connect(self.copy_report)
        bar.addWidget(copy_btn)

        save_btn = QPushButton("Save Report")
        save_btn.clicked.connect(self.save_report)
        bar.addWidget(save_btn)

        layout.addLayout(bar)
        self.tabs.addTab(tab, "Fix Boot")

    def init_chroot_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.chroot_output = QTextEdit(readOnly=True)
        btn = QPushButton("Choose Root Partition…")
        btn.clicked.connect(self.choose_partition)
        layout.addWidget(btn)
        layout.addWidget(self.chroot_output)
        self.tabs.addTab(tab, "Chroot Helper")

    def init_recovery_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.recovery_output = QTextEdit(readOnly=True)
        btn = QPushButton("Start Recovery Mode (Root)")
        btn.clicked.connect(self.run_recovery)
        layout.addWidget(btn)
        layout.addWidget(self.recovery_output)
        self.tabs.addTab(tab, "Recovery Mode")

    def init_sysinfo_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.sysinfo_output = QTextEdit(readOnly=True)
        btn = QPushButton("Fetch System Info")
        btn.clicked.connect(self.run_sysinfo)
        layout.addWidget(btn)
        layout.addWidget(self.sysinfo_output)
        self.tabs.addTab(tab, "System Info")

    def init_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.log_output = QTextEdit(readOnly=True)
        layout.addWidget(self.log_output)
        self.tabs.addTab(tab, "Logs")

    def set_status(self, msg: str):
        self.status.showMessage(msg, 5000)

    def log_message(self, message: str):
        self.log_output.append(f"[LOG] {message}")

    def colorize(self, text: str) -> str:
        html = []
        for line in text.splitlines():
            prefix = line[:1]
            if prefix in self.COLOR_MAP:
                color = self.COLOR_MAP[prefix]
                html.append(f'<span style="color:{color}; font-weight:bold;">{line}</span>')
            else:
                html.append(line.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"))
        return '<pre style="font-family: monospace;">' + "<br>".join(html) + "</pre>"

    def analyze_fix_output(self, out: str) -> str:
        summary = []
        if "Initcpio image generation successful" in out:
            summary.append("✔ Initramfs rebuilt")
        if "Generating grub configuration file" in out:
            summary.append("✔ GRUB config generated")
        if "Boot entries updated" in out or "Adding boot menu entry" in out:
            summary.append("✔ Boot entries updated")
        if summary:
            out += "\n\n--- Summary ---\n" + "\n".join(summary)
        return out

    def run_scan(self):
        self.scan_output.setHtml("<i>Scanning…</i>")
        self.set_status("Running system scan...")
        th = WorkerThread(BootScanner.run_scan)
        th.finished.connect(lambda txt: [
            self.scan_output.setHtml(self.colorize(txt)),
            self.log_message("System scan finished."),
            self.set_status("System scan finished.")
        ])
        self.threads.append(th)
        th.start()

    def run_fix(self):
        if QMessageBox.question(self, "Confirm", "Run fix as root?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        self.fix_output.setHtml("<i>Running fix…</i>")
        self.set_status("Running boot fix...")
        th = WorkerThread(BootFixer.run_fix)
        th.finished.connect(lambda txt: [
            self.fix_output.setHtml(self.colorize(self.analyze_fix_output(txt))),
            self.log_message("Boot repair finished."),
            self.set_status("Boot repair finished.")
        ])
        self.threads.append(th)
        th.start()

    def choose_partition(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Partition Device", "/dev", "Block Device (*)")
        if path:
            script = ChrootHelper.chroot_script(path)
            self.chroot_output.setPlainText(script)
            self.log_message(f"Chroot script generated for {path}")
            self.set_status(f"Chroot script generated for {path}")

    def run_recovery(self):
        self.recovery_output.setPlainText("Running recovery…")
        self.set_status("Running recovery mode...")
        th = WorkerThread(RecoveryManager.run)
        th.finished.connect(lambda txt: [
            self.recovery_output.setPlainText(txt),
            self.log_message("Recovery mode finished."),
            self.set_status("Recovery mode finished.")
        ])
        self.threads.append(th)
        th.start()

    def run_sysinfo(self):
        info = SystemInfoFetcher.fetch()
        self.sysinfo_output.setPlainText(info)
        self.log_message("System info fetched.")
        self.set_status("System info fetched.")

    def copy_report(self):
        QApplication.clipboard().setText(self.fix_output.toPlainText())
        self.log_message("Report copied to clipboard.")
        self.set_status("Report copied to clipboard.")

    def save_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Report", "bootfix-report.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w") as f:
                f.write(self.fix_output.toPlainText())
            self.log_message(f"Report saved to {path}")
            self.set_status(f"Report saved to {path}")


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Noto Sans", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
