import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QPixmap, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

from widget import FlightWidget


def _make_tray_icon():
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setFont(QFont('Arial', 20))
    p.drawText(px.rect(), Qt.AlignCenter, '✈')
    p.end()
    return QIcon(px)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = FlightWidget()
    widget.show()

    tray = QSystemTrayIcon(_make_tray_icon(), app)
    tray.setToolTip('Flight Alerts')

    menu = QMenu()
    show_action = QAction('Show Widget')
    show_action.triggered.connect(widget.show)
    menu.addAction(show_action)
    menu.addSeparator()
    quit_action = QAction('Quit')
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: widget.show() if reason == QSystemTrayIcon.Trigger else None
    )
    tray.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
