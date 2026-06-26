from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

import airports as db


POPUP_STYLE = """
QListWidget {
    background: white;
    border: 1.5px solid #BFDBFE;
    border-radius: 10px;
    padding: 4px;
    outline: 0;
    font-family: -apple-system, sans-serif;
}
QListWidget::item {
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    color: #1E293B;
    border-bottom: 1px solid #F1F5F9;
}
QListWidget::item:last-child { border-bottom: none; }
QListWidget::item:hover, QListWidget::item:selected {
    background: #EFF6FF;
    color: #1B3A5C;
}
"""

EDIT_STYLE = """
QLineEdit#iata {
    font-size: 15px;
    font-weight: bold;
    color: #1B3A5C;
    background: #F0F7FF;
    border: 1.5px solid #BFDBFE;
    border-radius: 8px;
    padding: 7px 10px;
    text-align: center;
}
QLineEdit#iata:focus {
    background: white;
    border: 1.5px solid #3B82F6;
    font-size: 13px;
    font-weight: normal;
    color: #334155;
}
"""


class AirportField(QWidget):
    """Single-line airport input with live autocomplete dropdown."""

    code_selected = pyqtSignal(str)

    def __init__(self, placeholder='City, country or IATA…', parent=None):
        super().__init__(parent)
        self._selected_iata = ''

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.edit = QLineEdit()
        self.edit.setObjectName('iata')
        self.edit.setPlaceholderText(placeholder)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setStyleSheet(EDIT_STYLE)
        lay.addWidget(self.edit)

        self._popup = QListWidget()
        self._popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self._popup.setFocusPolicy(Qt.NoFocus)
        self._popup.setAttribute(Qt.WA_ShowWithoutActivating)
        self._popup.setStyleSheet(POPUP_STYLE)
        self._popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.edit.textChanged.connect(self._suggest)
        self._popup.itemClicked.connect(self._pick)

    # ── public API ────────────────────────────────────────────────────────

    def text(self) -> str:
        """Always returns the 3-letter IATA code (or raw text if not yet selected)."""
        return (self._selected_iata or self.edit.text().strip().upper())[:3]

    def clear(self):
        self._selected_iata = ''
        self.edit.clear()
        self._popup.hide()

    def setText(self, code: str):
        self._selected_iata = code.upper()
        self.edit.blockSignals(True)
        self.edit.setText(code.upper())
        self.edit.blockSignals(False)

    # ── internal ──────────────────────────────────────────────────────────

    def _suggest(self, text: str):
        t = text.strip()
        if len(t) < 2:
            self._popup.hide()
            return

        results = db.search(t)
        if not results:
            self._popup.hide()
            return

        self._popup.clear()
        for r in results:
            label = f"  {r['iata']}  ·  {r['city']}, {r['country']}  —  {r['name']}"
            item  = QListWidgetItem(label)
            item.setData(Qt.UserRole, r['iata'])
            self._popup.addItem(item)

        width  = max(self.edit.width(), 320)
        height = min(self._popup.count() * 38 + 10, 220)
        self._popup.setFixedWidth(width)
        self._popup.setFixedHeight(height)

        pos = self.edit.mapToGlobal(QPoint(0, self.edit.height() + 2))
        self._popup.move(pos)
        if not self._popup.isVisible():
            self._popup.show()

    def _pick(self, item: QListWidgetItem):
        iata = item.data(Qt.UserRole)
        self._selected_iata = iata
        self.edit.blockSignals(True)
        self.edit.setText(iata)
        self.edit.blockSignals(False)
        self._popup.hide()
        self.code_selected.emit(iata)

    def hideEvent(self, event):
        self._popup.hide()
        super().hideEvent(event)
