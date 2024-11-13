# main.py

import sys
from PyQt5.QtWidgets import QApplication
from gui.gui import FinancialApp
# V3 vv
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinancialApp()
    window.show()
    sys.exit(app.exec_())
