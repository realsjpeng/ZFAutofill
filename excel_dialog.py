"""Excel / xls column-picker dialog — choose sheet, two columns, row range."""

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from i18n import I18n


class ExcelColumnDialog(QDialog):
    """Let the user choose a sheet, two columns, and a row range."""

    def __init__(self, sheets, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.sheets = sheets  # dict[str, list[list[str]]]
        self.setWindowTitle(i18n.t("select_columns"))
        self.resize(820, 540)
        self._build_ui()
        if sheets:
            self._on_sheet_changed(next(iter(sheets)))
            self._update_preview()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Sheet selector
        sheet_row = QHBoxLayout()
        sheet_row.addWidget(QLabel(self.i18n.t("sheet") + ":"))
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(list(self.sheets.keys()))
        self.sheet_combo.currentTextChanged.connect(self._on_sheet_changed)
        sheet_row.addWidget(self.sheet_combo, 1)
        layout.addLayout(sheet_row)

        # Column 1
        col1_row = QHBoxLayout()
        col1_row.addWidget(QLabel(self.i18n.t("column_1") + ":"))
        self.col1_combo = QComboBox()
        col1_row.addWidget(self.col1_combo, 1)
        layout.addLayout(col1_row)

        # Column 2
        col2_row = QHBoxLayout()
        col2_row.addWidget(QLabel(self.i18n.t("column_2") + ":"))
        self.col2_combo = QComboBox()
        col2_row.addWidget(self.col2_combo, 1)
        layout.addLayout(col2_row)

        # Row range
        range_row = QHBoxLayout()
        range_row.addWidget(QLabel(self.i18n.t("start_row") + ":"))
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        range_row.addWidget(self.start_spin)
        range_row.addWidget(QLabel(self.i18n.t("end_row") + ":"))
        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        range_row.addWidget(self.end_spin)
        range_row.addStretch(1)
        layout.addLayout(range_row)

        # Preview table
        self.preview = QTableWidget()
        self.preview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.preview.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.preview, 1)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton(self.i18n.t("ok"))
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(self.i18n.t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        # Live preview updates
        self.start_spin.valueChanged.connect(self._update_preview)
        self.end_spin.valueChanged.connect(self._update_preview)
        self.col1_combo.currentIndexChanged.connect(self._update_preview)
        self.col2_combo.currentIndexChanged.connect(self._update_preview)

    def _on_sheet_changed(self, name):
        data = self.sheets.get(name, [])
        ncols = max((len(r) for r in data), default=0)

        self.col1_combo.blockSignals(True)
        self.col2_combo.blockSignals(True)
        self.col1_combo.clear()
        self.col2_combo.clear()
        for i in range(ncols):
            sample = data[0][i] if data and i < len(data[0]) else ""
            text = f"{self._col_label(i)}  ({sample})"
            self.col1_combo.addItem(text, i)
            self.col2_combo.addItem(text, i)
        if ncols >= 2:
            self.col1_combo.setCurrentIndex(0)
            self.col2_combo.setCurrentIndex(1)
        elif ncols == 1:
            self.col1_combo.setCurrentIndex(0)
        self.col1_combo.blockSignals(False)
        self.col2_combo.blockSignals(False)

        nrows = len(data)
        self.start_spin.setMaximum(max(nrows, 1))
        self.end_spin.setMaximum(max(nrows, 1))
        self.start_spin.setValue(1)
        self.end_spin.setValue(nrows)
        self._update_preview()

    def _update_preview(self, *_):
        name = self.sheet_combo.currentText()
        data = self.sheets.get(name, [])
        s = max(self.start_spin.value() - 1, 0)
        e = max(self.end_spin.value(), s)
        view = data[s:e]
        preview_n = min(60, len(view))
        ncols = max((len(r) for r in view), default=0)
        self.preview.clear()
        self.preview.setRowCount(preview_n)
        self.preview.setColumnCount(ncols)
        self.preview.setHorizontalHeaderLabels(
            [self._col_label(i) for i in range(ncols)]
        )
        for r in range(preview_n):
            row = view[r]
            for c in range(ncols):
                val = row[c] if c < len(row) else ""
                self.preview.setItem(r, c, QTableWidgetItem(str(val)))
        self.preview.setVerticalHeaderLabels(
            [str(s + i + 1) for i in range(preview_n)]
        )

    @staticmethod
    def _col_label(i: int) -> str:
        s = ""
        i += 1
        while i > 0:
            i, rem = divmod(i - 1, 26)
            s = chr(ord("A") + rem) + s
        return s

    def get_values(self):
        s = self.start_spin.value() - 1
        e = self.end_spin.value()
        c1 = self.col1_combo.currentData()
        c2 = self.col2_combo.currentData()
        data = self.sheets[self.sheet_combo.currentText()]
        if c1 is None or c2 is None or c1 == c2:
            return [], []
        col1, col2 = [], []
        for r in range(s, min(e, len(data))):
            row = data[r]
            if c1 < len(row):
                col1.append(str(row[c1]).strip())
            if c2 < len(row):
                col2.append(str(row[c2]).strip())
        return col1, col2
