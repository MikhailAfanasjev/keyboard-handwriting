from PyQt5 import QtWidgets, uic
import sys

from handlers import connect_interface_handlers


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = uic.loadUi("qt_forms/main_frame.ui")
    gp_dialog = uic.loadUi("qt_forms/generate_password_dialog.ui")
    connect_interface_handlers(win, gp_dialog)
    win.show()
    sys.exit(app.exec())
