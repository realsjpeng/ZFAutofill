"""GUI — CustomWebEnginePage, MainWindow, and stylesheet."""

import json
import os
import re
import sys
from pathlib import Path

from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from excel_dialog import ExcelColumnDialog
from file_reader import read_excel_sheets, read_txt
from icons import make_icon
from i18n import I18n
from run_scores import run_input_scores


class CustomWebEnginePage(QWebEnginePage):
    """Strip ``target="_blank"`` and block new-window popups."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view_ref = None
        self.loadFinished.connect(self.modify_links)

    def modify_links(self):
        js = (
            "var links = document.querySelectorAll('a[target=\"_blank\"]');"
            "links.forEach(function(link) { link.removeAttribute('target'); });"
        )
        self.runJavaScript(js)

    def createWindow(self, _type):
        if self.view_ref is not None:
            return self
        return None


STYLESHEET = """
QWidget {
    background: #F1F5F9;
    color: #0F172A;
    font-family: "Inter", "Microsoft YaHei", "PingFang SC",
                 "Hiragino Sans GB", "Segoe UI", sans-serif;
}

QFrame#card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

QLineEdit#addressEdit {
    padding: 0 14px 0 36px;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    background: #F8FAFC;
    font-size: 14px;
    color: #0F172A;
    selection-background-color: #6366F1;
    min-height: 36px;
}
QLineEdit#addressEdit:focus {
    border-color: #6366F1;
    background: #FFFFFF;
}
QLineEdit#addressEdit:hover {
    border-color: #CBD5E1;
}

QPushButton#secondaryButton {
    padding: 7px 14px;
    border: 1px solid #E2E8F0;
    border-radius: 9px;
    background: #FFFFFF;
    color: #334155;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
}
QPushButton#secondaryButton:hover {
    background: #F8FAFC;
    border-color: #CBD5E1;
    color: #0F172A;
}
QPushButton#secondaryButton:pressed {
    background: #E2E8F0;
}

QPushButton#primaryButton {
    padding: 7px 16px;
    border: none;
    border-radius: 9px;
    background: #6366F1;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    min-height: 28px;
}
QPushButton#primaryButton:hover  { background: #4F46E5; }
QPushButton#primaryButton:pressed{ background: #4338CA; }

QPushButton#runButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #10B981, stop:1 #059669
    );
    color: #FFFFFF;
    border: none;
    border-radius: 24px;
    min-height: 46px;
    min-width: 170px;
    font-size: 15px;
    font-weight: 600;
    padding: 6px 30px;
    letter-spacing: 0.3px;
}
QPushButton#runButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #059669, stop:1 #047857
    );
}
QPushButton#runButton:pressed { background: #047857; }

QLabel#statusLabel {
    color: #475569;
    font-size: 13px;
    padding: 0 4px;
}
"""


class MainWindow(QWidget):
    def __init__(self, i18n: I18n, config: dict, config_path: str):
        super().__init__()
        self.i18n = i18n
        self.config = config
        self.config_path = config_path
        self.current_file = None

        self.setWindowTitle(i18n.t("title"))
        self.resize(1240, 820)
        self._build_ui()
        self.setStyleSheet(STYLESHEET)
        self._update_status()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        # ---- Top toolbar card ----
        toolbar_card = QFrame()
        toolbar_card.setObjectName("card")
        toolbar = QHBoxLayout(toolbar_card)
        toolbar.setContentsMargins(8, 8, 8, 8)
        toolbar.setSpacing(8)

        self.open_btn = QPushButton(self.i18n.t("open"))
        self.open_btn.setIcon(make_icon("folder", "#475569"))
        self.open_btn.setIconSize(QSize(16, 16))
        self.open_btn.setObjectName("secondaryButton")
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.setToolTip(self.i18n.t("tooltip_open"))
        self.open_btn.clicked.connect(self.on_open)
        toolbar.addWidget(self.open_btn)

        self.address_edit = QLineEdit()
        self.address_edit.setObjectName("addressEdit")
        self.address_edit.setText(self.config.get("base_url", ""))
        self.address_edit.setPlaceholderText(self.i18n.t("address"))
        self.address_edit.setToolTip(self.i18n.t("tooltip_address"))
        self.address_edit.setClearButtonEnabled(True)
        self.address_edit.addAction(
            make_icon("globe", "#94A3B8", 16),
            QLineEdit.LeadingPosition,
        )
        self.address_edit.returnPressed.connect(self.on_go)
        toolbar.addWidget(self.address_edit, 1)

        self.go_btn = QPushButton(self.i18n.t("go"))
        self.go_btn.setIcon(make_icon("arrow_right", "#FFFFFF", 16))
        self.go_btn.setIconSize(QSize(16, 16))
        self.go_btn.setObjectName("primaryButton")
        self.go_btn.setCursor(Qt.PointingHandCursor)
        self.go_btn.setToolTip(self.i18n.t("tooltip_go"))
        self.go_btn.clicked.connect(self.on_go)
        toolbar.addWidget(self.go_btn)

        root.addWidget(toolbar_card)

        # ---- Web view ----
        self.view = QWebEngineView()
        self.page = CustomWebEnginePage()
        self.page.view_ref = self.view
        self.view.setPage(self.page)
        self.view.urlChanged.connect(self._on_url_changed)
        url = self.config.get("base_url")
        if url:
            self.view.setUrl(QUrl(url))
        root.addWidget(self.view, 1)

        # ---- Bottom card: file info + Run button ----
        bottom_card = QFrame()
        bottom_card.setObjectName("card")
        bottom = QHBoxLayout(bottom_card)
        bottom.setContentsMargins(10, 8, 8, 8)
        bottom.setSpacing(8)

        file_info = QHBoxLayout()
        file_info.setSpacing(8)
        self.file_icon_label = QLabel()
        self.file_icon_label.setPixmap(
            make_icon("file", "#64748B", 16).pixmap(16, 16)
        )
        self.file_icon_label.setFixedSize(16, 16)
        file_info.addWidget(self.file_icon_label)

        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        file_info.addWidget(self.status_label, 1)

        bottom.addLayout(file_info, 1)

        self.run_btn = QPushButton(self.i18n.t("run"))
        self.run_btn.setObjectName("runButton")
        self.run_btn.setIcon(make_icon("play", "#FFFFFF", 18))
        self.run_btn.setIconSize(QSize(18, 18))
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.setToolTip(self.i18n.t("tooltip_run"))
        self.run_btn.clicked.connect(self.on_run)

        # Subtle green drop-shadow to make the Run button pop
        shadow = QGraphicsDropShadowEffect(self.run_btn)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(16, 185, 129, 110))
        self.run_btn.setGraphicsEffect(shadow)

        bottom.addWidget(self.run_btn)

        root.addWidget(bottom_card)

    # ---------------- helpers ----------------

    def _update_status(self):
        path = Path(self.current_file).name if self.current_file else "—"
        self.status_label.setText(f"{self.i18n.t('current_file')}: {path}")

    def _on_url_changed(self, url: QUrl):
        s = url.toString()
        if s and s != "about:blank":
            self.address_edit.setText(s)

    def _save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, self.i18n.t("error"), str(e))

    # ---------------- slots ----------------

    def on_go(self):
        url = self.address_edit.text().strip()
        if not url:
            return
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", url):
            url = "http://" + url
        self.view.setUrl(QUrl(url))
        # Persist immediately so the next launch opens this URL.
        self.config["base_url"] = url
        self._save_config()

    def on_open(self):
        start_dir = os.path.dirname(self.current_file) if self.current_file else "."
        if not os.path.isdir(start_dir):
            start_dir = "."
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.i18n.t("open"),
            start_dir,
            self.i18n.t("open_filter"),
        )
        if not path:
            return

        ext = Path(path).suffix.lower()
        if ext == ".txt":
            self.current_file = path
            self._update_status()
            return

        if ext in (".xls", ".xlsx"):
            try:
                sheets = read_excel_sheets(path)
            except RuntimeError:
                key = "missing_openpyxl" if ext == ".xlsx" else "missing_xlrd"
                QMessageBox.critical(self, self.i18n.t("error"), self.i18n.t(key))
                return
            except Exception as e:
                QMessageBox.critical(
                    self, self.i18n.t("error"),
                    self.i18n.t("read_file_error", str(e)),
                )
                return
            if not sheets:
                QMessageBox.warning(
                    self, self.i18n.t("error"),
                    self.i18n.t("read_file_error", "No sheets found"),
                )
                return

            dlg = ExcelColumnDialog(sheets, self.i18n, self)
            if dlg.exec_() != QDialog.Accepted:
                return

            col1, col2 = dlg.get_values()
            if not col1 or not col2:
                QMessageBox.warning(
                    self, self.i18n.t("error"), self.i18n.t("no_data")
                )
                return

            self.current_file = path
            self.config["last_sheet"] = dlg.sheet_combo.currentText()
            self.config["last_col1"] = dlg.col1_combo.currentData()
            self.config["last_col2"] = dlg.col2_combo.currentData()
            self.config["last_start"] = dlg.start_spin.value()
            self.config["last_end"] = dlg.end_spin.value()
            self._save_config()
            self._update_status()
            return

        QMessageBox.warning(
            self, self.i18n.t("error"),
            self.i18n.t("file_type_error", ext),
        )

    def on_run(self):
        try:
            if not self.current_file or not os.path.exists(self.current_file):
                QMessageBox.critical(
                    self,
                    self.i18n.t("error"),
                    self.i18n.t("file_not_found", self.current_file or ""),
                )
                return

            ext = Path(self.current_file).suffix.lower()
            if ext == ".txt":
                ps, qm = read_txt(self.current_file)
            elif ext in (".xls", ".xlsx"):
                sheets = read_excel_sheets(self.current_file)
                sheet_name = self.config.get("last_sheet")
                if not sheet_name or sheet_name not in sheets:
                    sheet_name = next(iter(sheets))
                c1 = self.config.get("last_col1", 0)
                c2 = self.config.get("last_col2", 1)
                s = max(self.config.get("last_start", 1) - 1, 0)
                e = self.config.get("last_end", len(sheets[sheet_name]))
                data = sheets[sheet_name]
                ps, qm = [], []
                for r in range(s, min(e, len(data))):
                    row = data[r]
                    if c1 < len(row):
                        ps.append(str(row[c1]).strip())
                    if c2 < len(row):
                        qm.append(str(row[c2]).strip())
            else:
                QMessageBox.warning(
                    self, self.i18n.t("error"),
                    self.i18n.t("file_type_error", ext),
                )
                return

            if not ps or not qm:
                QMessageBox.warning(
                    self, self.i18n.t("error"), self.i18n.t("no_data")
                )
                return

            run_input_scores(self.view, ps, qm)
        except Exception as e:
            QMessageBox.critical(self, self.i18n.t("error"), str(e))
