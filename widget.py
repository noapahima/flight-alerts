import threading
import time
import uuid
from datetime import datetime

from PyQt5.QtCore import QDate, QObject, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QLinearGradient
from PyQt5.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QDateEdit, QDialog,
    QDialogButtonBox, QFormLayout, QFrame, QGraphicsDropShadowEffect,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QRadioButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

import checker
import notifier
import storage
from airport_input import AirportField

# ── Stylesheet ─────────────────────────────────────────────────────────────

STYLE = """
QWidget#root {
    background: #EEF2F9;
    border-radius: 20px;
}

/* ── Header ─────────────────────────────── */
QWidget#header {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #09142A, stop:0.55 #0D2245, stop:1 #152F62);
    border-radius: 18px 18px 0 0;
}
QLabel#title {
    color: white;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 0.5px;
    background: transparent;
}
QLabel#subtitle {
    color: rgba(255,255,255,0.32);
    font-size: 8px;
    letter-spacing: 3px;
    background: transparent;
}
QPushButton#hdr_btn {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.11);
    border-radius: 14px;
    color: rgba(255,255,255,0.55);
    font-size: 13px;
    padding: 0;
}
QPushButton#hdr_btn:hover {
    background: rgba(255,255,255,0.16);
    color: white;
}

/* ── Body ────────────────────────────────── */
QWidget#body { background: #EEF2F9; }

/* ── Form card ───────────────────────────── */
QFrame#form_card {
    background: white;
    border-radius: 16px;
    border: 1px solid #DDE6F4;
}
QLabel#field_lbl {
    color: #8899B8;
    font-size: 8px;
    font-weight: bold;
    letter-spacing: 2px;
    background: transparent;
}
QLineEdit, QDateEdit, QSpinBox {
    border: 1.5px solid #DDE6F4;
    border-radius: 9px;
    padding: 8px 11px;
    background: #F7FAFF;
    color: #0F172A;
    font-size: 13px;
    selection-background-color: #BAD7FF;
}
QLineEdit:focus, QDateEdit:focus, QSpinBox:focus {
    border: 1.5px solid #3B82F6;
    background: white;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 16px;
    border: none;
    background: transparent;
}
QPushButton#add_btn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1D4ED8, stop:1 #1E40AF);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 11px;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QPushButton#add_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2563EB, stop:1 #1D4ED8);
}
QPushButton#add_btn:pressed { background: #1E3A8A; }

/* ── Section ─────────────────────────────── */
QLabel#section_title {
    color: #94A3B8;
    font-size: 8px;
    font-weight: bold;
    letter-spacing: 2.5px;
    background: transparent;
}

/* ── Footer ──────────────────────────────── */
QWidget#footer {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #09142A, stop:1 #0D2245);
    border-radius: 0 0 18px 18px;
}
QLabel#status_lbl {
    color: rgba(255,255,255,0.42);
    font-size: 10px;
    background: transparent;
}

/* ── Radios & checkboxes ─────────────────── */
QRadioButton {
    font-size: 12px; color: #475569; background: transparent; spacing: 6px;
}
QRadioButton::indicator {
    width: 14px; height: 14px; border-radius: 7px;
    border: 1.5px solid #CBD5E1; background: white;
}
QRadioButton::indicator:checked {
    border: 1.5px solid #3B82F6; background: #3B82F6;
}
QCheckBox { font-size: 12px; color: #475569; background: transparent; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px; border-radius: 4px;
    border: 1.5px solid #CBD5E1; background: white;
}
QCheckBox::indicator:checked {
    border: 1.5px solid #3B82F6; background: #3B82F6;
}

/* ── Scroll ──────────────────────────────── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: transparent; width: 4px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #CBD5E1; border-radius: 2px; min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


# ── Alert card ──────────────────────────────────────────────────────────────

class AlertCard(QFrame):
    removed = pyqtSignal(str)

    def __init__(self, alert):
        super().__init__()
        self.alert_id = alert['id']
        self._blue    = '#3B82F6'
        self._green   = '#10B981'
        self._border  = self._blue
        self.setObjectName('alert_card')
        self._apply_style()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(5)

        # ── Row 1: route + delete ──
        top = QHBoxLayout(); top.setSpacing(4)

        route = QLabel(f'{alert["origin"]}  ✈  {alert["destination"]}')
        route.setStyleSheet(
            'font-size:16px;font-weight:bold;color:#0F2444;background:transparent;')

        top.addWidget(route); top.addStretch()

        x = QPushButton('✕')
        x.setFixedSize(20, 20)
        x.setStyleSheet(
            'border:none;color:#CBD5E1;background:transparent;font-size:11px;')
        x.clicked.connect(lambda: self.removed.emit(self.alert_id))
        x.setCursor(Qt.PointingHandCursor)
        top.addWidget(x)
        lay.addLayout(top)

        # ── Row 2: badges ──
        badges = QHBoxLayout(); badges.setSpacing(5)
        dates = alert['date']
        if alert.get('return_date'):
            dates += f' ↩ {alert["return_date"]}'
        badges.addWidget(self._badge(f'📅 {dates}',         '#EFF6FF', '#3B82F6'))
        badges.addWidget(self._badge(f'Max ${alert["max_price"]:.0f}', '#FFF7ED', '#F97316'))
        if alert.get('include_luggage'):
            badges.addWidget(self._badge('🧳 Bag', '#F0FDF4', '#10B981'))
        badges.addStretch()
        lay.addLayout(badges)

        # ── Row 3: live price ──
        self.price_lbl = QLabel('⏳  Waiting for first check…')
        self.price_lbl.setStyleSheet(
            'color:#94A3B8;font-size:11px;font-style:italic;background:transparent;')
        lay.addWidget(self.price_lbl)

    def _badge(self, text, bg, fg):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f'background:{bg};color:{fg};font-size:10px;font-weight:bold;'
            f'border-radius:5px;padding:2px 7px;border:1px solid {fg}33;')
        return lbl

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame#alert_card {{
                background: white;
                border-radius: 12px;
                border: 1px solid #E8EEF6;
                border-left: 4px solid {self._border};
            }}
            QLabel {{ background: transparent; }}
        """)

    def update_price(self, price, currency, below, source=''):
        src = f' · {source}' if source else ''
        if below:
            self._border = self._green
            self._apply_style()
            self.price_lbl.setText(f'🟢  {currency} {price:.0f}  ·  Alert sent!{src}')
            self.price_lbl.setStyleSheet(
                'color:#10B981;font-size:11px;font-weight:bold;background:transparent;')
        else:
            self.price_lbl.setText(
                f'💰  {currency} {price:.0f}  ·  {datetime.now().strftime("%H:%M")}{src}')
            self.price_lbl.setStyleSheet(
                'color:#475569;font-size:11px;background:transparent;')

    def mark_error(self, msg):
        self.price_lbl.setText(f'⚠  {msg[:40]}')
        self.price_lbl.setStyleSheet('color:#EF4444;font-size:10px;background:transparent;')


# ── Settings dialog ────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, config, delete_cb, parent=None):
        super().__init__(parent)
        self.config    = config
        self.delete_cb = delete_cb
        self.setWindowTitle('Active Alerts & Settings')
        self.setMinimumWidth(460)
        self.setStyleSheet("""
            QDialog { background: #F7F9FC; }
            QLabel { color: #1E293B; }
            QLineEdit {
                border: 1.5px solid #DDE6F4; border-radius: 8px;
                padding: 7px 10px; background: #F7FAFF; color: #0F172A; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #3B82F6; background: white; }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 22, 22, 22)
        lay.setSpacing(14)

        t1 = QLabel('ACTIVE ALERTS')
        t1.setStyleSheet('font-size:9px;font-weight:bold;color:#94A3B8;letter-spacing:2px;')
        lay.addWidget(t1)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setMaximumHeight(260)
        self._scroll.setStyleSheet(
            'QScrollArea{border:1.5px solid #DDE6F4;border-radius:10px;background:white;}')
        self._inner = QWidget(); self._inner.setStyleSheet('background:white;')
        self._ilay  = QVBoxLayout(self._inner)
        self._ilay.setContentsMargins(10, 10, 10, 10); self._ilay.setSpacing(6)
        self._scroll.setWidget(self._inner)
        lay.addWidget(self._scroll)
        self._populate()

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet('color:#E2E8F0;margin:2px 0;'); lay.addWidget(sep)

        t2 = QLabel('RESEND API KEY')
        t2.setStyleSheet('font-size:9px;font-weight:bold;color:#94A3B8;letter-spacing:2px;')
        lay.addWidget(t2)

        form = QFormLayout(); form.setSpacing(8)
        self.resend_e = QLineEdit(config.get('resend_api_key', ''))
        self.resend_e.setPlaceholderText('re_xxxxxxxxxxxxxxxxxxxx')
        self.resend_e.setEchoMode(QLineEdit.Password)
        form.addRow('API Key:', self.resend_e)
        lay.addLayout(form)

        note = QLabel('Free at resend.com — 3,000 emails/month')
        note.setStyleSheet('font-size:10px;color:#94A3B8;'); lay.addWidget(note)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _populate(self):
        while self._ilay.count():
            item = self._ilay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        alerts = self.config.get('alerts', [])
        if not alerts:
            e = QLabel('No active alerts yet.')
            e.setStyleSheet('color:#94A3B8;font-size:12px;padding:8px;')
            self._ilay.addWidget(e)
            return

        for a in alerts:
            row = QFrame()
            row.setStyleSheet(
                'QFrame{background:#F8FAFC;border-radius:8px;border:1px solid #E8EEF6;}')
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 8, 8); rl.setSpacing(6)

            tt  = '↔' if a.get('trip_type') == 'RT' else '→'
            bag = '  🧳' if a.get('include_luggage') else ''
            dt  = a['date'] + (f'  ↩ {a["return_date"]}' if a.get('return_date') else '')
            info = QLabel(
                f"<b>{a['origin']} {tt} {a['destination']}</b>{bag}<br>"
                f"<span style='color:#94A3B8;font-size:11px;'>"
                f"📅 {dt}&nbsp;&nbsp;💰 Max ${a['max_price']:.0f}&nbsp;&nbsp;📧 {a['email']}"
                f"</span>")
            info.setStyleSheet('font-size:12px;color:#1E293B;background:transparent;')
            info.setTextFormat(Qt.RichText)
            rl.addWidget(info, 1)

            x = QPushButton('✕')
            x.setFixedSize(26, 26)
            x.setStyleSheet(
                'border:none;color:#EF4444;background:transparent;'
                'font-weight:bold;font-size:13px;')
            x.setCursor(Qt.PointingHandCursor)
            x.clicked.connect(lambda _, aid=a['id']: self._delete(aid))
            rl.addWidget(x)
            self._ilay.addWidget(row)

    def _delete(self, aid):
        self.delete_cb(aid)
        self._populate()

    def _save(self):
        self.config['resend_api_key'] = self.resend_e.text().strip()
        storage.save(self.config)
        self.accept()


# ── Signals ────────────────────────────────────────────────────────────────

class Signals(QObject):
    price_result = pyqtSignal(str, float, str, str, str, object)  # id, price, currency, source, url, all_results
    check_error  = pyqtSignal(str, str)
    status       = pyqtSignal(str)


# ── Main widget ────────────────────────────────────────────────────────────

class FlightWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.config    = storage.load()
        self.cards     = {}
        self._drag_pos = None
        self.sig       = Signals()
        self.sig.price_result.connect(self._on_price)
        self.sig.check_error.connect(self._on_error)
        self.sig.status.connect(self._on_status)
        self._build_ui()
        self._start_bg()

    # ── Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(360)
        self.setStyleSheet(STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        self.root = QWidget()
        self.root.setObjectName('root')
        outer.addWidget(self.root)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 8)
        self.root.setGraphicsEffect(shadow)

        main = QVBoxLayout(self.root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        main.addWidget(self._mk_header())
        main.addWidget(self._mk_body())
        main.addWidget(self._mk_footer())

        for a in self.config.get('alerts', []):
            self._insert_card(a)

        self.move(self.config.get('pos_x', 120), self.config.get('pos_y', 120))
        self.adjustSize()

    def _mk_header(self):
        w = QWidget(); w.setObjectName('header')
        h = QHBoxLayout(w)
        h.setContentsMargins(16, 14, 12, 14); h.setSpacing(6)

        left = QVBoxLayout(); left.setSpacing(2)
        title = QLabel('✈  FLIGHT ALERTS'); title.setObjectName('title')
        sub   = QLabel('LIVE PRICE TRACKING'); sub.setObjectName('subtitle')
        left.addWidget(title); left.addWidget(sub)
        h.addLayout(left); h.addStretch()

        for icon, tip, slot in [('⚙', 'Settings', self._open_settings),
                                  ('✕', 'Close',    self.hide)]:
            btn = QPushButton(icon); btn.setObjectName('hdr_btn')
            btn.setFixedSize(28, 28); btn.setToolTip(tip)
            btn.clicked.connect(slot); btn.setCursor(Qt.PointingHandCursor)
            h.addWidget(btn)
        return w

    def _mk_body(self):
        w = QWidget(); w.setObjectName('body')
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 14, 12, 10); lay.setSpacing(12)

        lay.addWidget(self._mk_form())

        sec = QLabel('ACTIVE ALERTS'); sec.setObjectName('section_title')
        lay.addWidget(sec)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(280)
        scroll.setMaximumHeight(600)
        self._cards_w = QWidget()
        self._cards_w.setStyleSheet('background:transparent;')
        self._cards_lay = QVBoxLayout(self._cards_w)
        self._cards_lay.setContentsMargins(0, 0, 0, 0); self._cards_lay.setSpacing(7)
        self._cards_lay.addStretch()
        scroll.setWidget(self._cards_w)
        lay.addWidget(scroll)
        return w

    def _mk_form(self):
        card = QFrame(); card.setObjectName('form_card')
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(14, 14, 14, 14); lay.setSpacing(10)

        # ── Route ──
        def airport_col(lbl_text, ph):
            v = QVBoxLayout(); v.setSpacing(3)
            lbl = QLabel(lbl_text); lbl.setObjectName('field_lbl')
            f = AirportField(ph)
            v.addWidget(lbl); v.addWidget(f)
            return v, f

        route_row = QHBoxLayout(); route_row.setSpacing(8)
        fc, self.origin_e = airport_col('FROM', 'City or IATA…')
        tc, self.dest_e   = airport_col('TO',   'City or IATA…')
        arrow = QLabel('✈')
        arrow.setStyleSheet(
            'font-size:20px;color:#3B82F6;background:transparent;padding-top:16px;')
        arrow.setAlignment(Qt.AlignCenter)
        route_row.addLayout(fc); route_row.addWidget(arrow); route_row.addLayout(tc)
        lay.addLayout(route_row)

        # ── Separator ──
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet('color:#EEF2F9;'); lay.addWidget(sep)

        # ── Trip type ──
        tt_row = QHBoxLayout(); tt_row.setSpacing(16)
        self.ow_radio = QRadioButton('One-way')
        self.rt_radio = QRadioButton('Round trip')
        self.ow_radio.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.ow_radio); grp.addButton(self.rt_radio)
        tt_row.addWidget(self.ow_radio)
        tt_row.addWidget(self.rt_radio)
        tt_row.addStretch()
        lay.addLayout(tt_row)

        # ── Dates ──
        dates_row = QHBoxLayout(); dates_row.setSpacing(10)

        dep_v = QVBoxLayout(); dep_v.setSpacing(3)
        dep_v.addWidget(self._fl('DEPARTURE'))
        self.date_e = QDateEdit()
        self.date_e.setCalendarPopup(True)
        self.date_e.setDate(QDate.currentDate().addMonths(1))
        self.date_e.setMinimumDate(QDate.currentDate().addDays(1))
        self.date_e.setDisplayFormat('dd MMM yyyy')
        dep_v.addWidget(self.date_e)
        dates_row.addLayout(dep_v)

        self._ret_w = QWidget()
        self._ret_w.setStyleSheet('background:transparent;')
        ret_v = QVBoxLayout(self._ret_w)
        ret_v.setContentsMargins(0, 0, 0, 0); ret_v.setSpacing(3)
        ret_v.addWidget(self._fl('RETURN'))
        self.ret_date_e = QDateEdit()
        self.ret_date_e.setCalendarPopup(True)
        self.ret_date_e.setDate(QDate.currentDate().addMonths(1).addDays(7))
        self.ret_date_e.setMinimumDate(QDate.currentDate().addDays(2))
        self.ret_date_e.setDisplayFormat('dd MMM yyyy')
        ret_v.addWidget(self.ret_date_e)
        self._ret_w.hide()
        dates_row.addWidget(self._ret_w)
        self.rt_radio.toggled.connect(self._ret_w.setVisible)
        lay.addLayout(dates_row)

        # ── Price + interval ──
        pi_row = QHBoxLayout(); pi_row.setSpacing(10)

        pv = QVBoxLayout(); pv.setSpacing(3)
        pv.addWidget(self._fl('MAX PRICE ($)'))
        self.price_e = QLineEdit()
        self.price_e.setPlaceholderText('500')
        pv.addWidget(self.price_e)

        iv = QVBoxLayout(); iv.setSpacing(3)
        iv.addWidget(self._fl('CHECK EVERY'))
        self.interval_e = QSpinBox()
        self.interval_e.setRange(1, 24)
        self.interval_e.setValue(self.config.get('check_interval_hours', 4))
        self.interval_e.setSuffix(' h')
        iv.addWidget(self.interval_e)

        pi_row.addLayout(pv, 2); pi_row.addLayout(iv, 1)
        lay.addLayout(pi_row)

        # ── Luggage ──
        bag_row = QHBoxLayout(); bag_row.setSpacing(8)
        self.luggage_cb = QCheckBox(); self.luggage_cb.setChecked(True)
        bag_lbl = QLabel('🧳  Include checked bag (23 kg)')
        bag_lbl.setStyleSheet('font-size:12px;color:#475569;background:transparent;')
        bag_row.addWidget(self.luggage_cb)
        bag_row.addWidget(bag_lbl)
        bag_row.addStretch()
        lay.addLayout(bag_row)

        # ── Email ──
        ev = QVBoxLayout(); ev.setSpacing(3)
        ev.addWidget(self._fl('ALERT EMAIL'))
        self.email_e = QLineEdit()
        self.email_e.setPlaceholderText('you@gmail.com')
        ev.addWidget(self.email_e)
        lay.addLayout(ev)

        btn = QPushButton('＋  ADD ALERT')
        btn.setObjectName('add_btn')
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._add_alert)
        lay.addWidget(btn)
        return card

    def _fl(self, text):
        lbl = QLabel(text); lbl.setObjectName('field_lbl')
        return lbl

    def _mk_footer(self):
        w = QWidget(); w.setObjectName('footer')
        h = QHBoxLayout(w); h.setContentsMargins(16, 8, 16, 8)
        self.status_lbl = QLabel('● Ready')
        self.status_lbl.setObjectName('status_lbl')
        h.addWidget(self.status_lbl)
        src = QLabel('Google · Skyscanner · Hulyo · El Al · Iberia')
        src.setStyleSheet('color:rgba(255,255,255,0.2);font-size:9px;background:transparent;')
        h.addStretch(); h.addWidget(src)
        return w

    # ── Logic ──────────────────────────────────────────────────────────────

    def _add_alert(self):
        origin    = self.origin_e.text().strip().upper()
        dest      = self.dest_e.text().strip().upper()
        date      = self.date_e.date().toString('yyyy-MM-dd')
        trip_type = 'RT' if self.rt_radio.isChecked() else 'OW'
        ret_date  = self.ret_date_e.date().toString('yyyy-MM-dd') if trip_type == 'RT' else ''
        price     = self.price_e.text().strip()
        email     = self.email_e.text().strip()
        incl_bag  = self.luggage_cb.isChecked()

        if len(origin) != 3 or len(dest) != 3:
            QMessageBox.warning(self, 'Invalid',
                'Use 3-letter IATA codes (TLV, LHR, JFK…)\n'
                'Tip: type a city or country name to see suggestions.')
            return
        if not price.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, 'Invalid', 'Enter a valid max price')
            return
        if '@' not in email:
            QMessageBox.warning(self, 'Invalid', 'Enter a valid email address')
            return

        self.config['check_interval_hours'] = self.interval_e.value()
        alert = {
            'id': str(uuid.uuid4())[:8],
            'origin': origin, 'destination': dest,
            'date': date, 'return_date': ret_date,
            'trip_type': trip_type, 'include_luggage': incl_bag,
            'max_price': float(price), 'email': email,
        }
        self.config['alerts'].append(alert)
        storage.save(self.config)
        self._insert_card(alert)
        self.origin_e.clear(); self.dest_e.clear(); self.price_e.clear()
        self.adjustSize()
        # Run an immediate check for this alert without waiting for the next cycle
        threading.Thread(target=self._check_single, args=(alert,), daemon=True).start()

    def _insert_card(self, alert):
        card = AlertCard(alert)
        card.removed.connect(self._remove_alert)
        self.cards[alert['id']] = card
        self._cards_lay.insertWidget(self._cards_lay.count() - 1, card)

    def _remove_alert(self, alert_id):
        self.config['alerts'] = [a for a in self.config['alerts'] if a['id'] != alert_id]
        storage.save(self.config)
        if c := self.cards.pop(alert_id, None):
            c.deleteLater()
        self.adjustSize()

    def _open_settings(self):
        dlg = SettingsDialog(self.config, delete_cb=self._remove_alert, parent=self)
        dlg.exec_()

    # ── Signals ────────────────────────────────────────────────────────────

    def _on_price(self, alert_id, price, currency, source, direct_url, all_results):
        card  = self.cards.get(alert_id)
        alert = next((a for a in self.config['alerts'] if a['id'] == alert_id), None)
        if not card or not alert:
            return
        below = price <= alert['max_price']
        card.update_price(price, currency, below, source)
        if alert.get('email') and self.config.get('resend_api_key'):
            try:
                if below:
                    notifier.send_price_alert(
                        self.config.get('resend_api_key', ''),
                        alert['email'], alert, price, currency, source, direct_url, all_results)
                else:
                    notifier.send_no_deal_summary(
                        self.config.get('resend_api_key', ''),
                        alert['email'], alert, price, currency, all_results)
            except Exception as e:
                self.sig.status.emit(f'⚠ Mail error: {str(e)[:40]}')

    def _on_error(self, alert_id, msg):
        if c := self.cards.get(alert_id):
            c.mark_error(msg)

    def _on_status(self, msg):
        self.status_lbl.setText(msg)

    # ── Background ─────────────────────────────────────────────────────────

    def _start_bg(self):
        def loop():
            self._run_checks()
            while True:
                hrs = self.config.get('check_interval_hours', 4)
                self.sig.status.emit(f'● Next check in {hrs}h')
                time.sleep(hrs * 3600)
                self._run_checks()
        threading.Thread(target=loop, daemon=True).start()

    def _check_single(self, alert):
        self.sig.status.emit(f'🔍  Checking {alert["origin"]} → {alert["destination"]}…')
        try:
            result = checker.get_cheapest_price(
                alert['origin'], alert['destination'], alert['date'],
                alert.get('return_date', ''), alert.get('trip_type', 'OW'),
                alert.get('include_luggage', False))
            if result:
                self.sig.price_result.emit(
                    alert['id'], result['min_price'],
                    result['currency'], result.get('source', ''),
                    result.get('url', ''), result.get('all', {}))
        except Exception as e:
            self.sig.check_error.emit(alert['id'], str(e))
        self.sig.status.emit(f'✓  Updated {datetime.now().strftime("%H:%M")}')

    def _run_checks(self):
        alerts = self.config.get('alerts', [])
        if not alerts:
            self.sig.status.emit('● Add an alert to start')
            return
        self.sig.status.emit('🔍  Checking prices…')
        for a in list(alerts):
            try:
                result = checker.get_cheapest_price(
                    a['origin'], a['destination'], a['date'],
                    a.get('return_date', ''), a.get('trip_type', 'OW'),
                    a.get('include_luggage', False))
                if result:
                    self.sig.price_result.emit(
                        a['id'], result['min_price'],
                        result['currency'], result.get('source', ''),
                        result.get('url', ''), result.get('all', {}))
            except Exception as e:
                self.sig.check_error.emit(a['id'], str(e))
        self.sig.status.emit(f'✓  Updated {datetime.now().strftime("%H:%M")}')

    # ── Drag ───────────────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None
        self.config.update({'pos_x': self.x(), 'pos_y': self.y()})
        storage.save(self.config)
