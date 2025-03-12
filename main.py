import sys
from PyQt5.QtWidgets import QApplication, QDialog

from customer-search-ui.py import   # Import the UI class

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QDialog()  # Create a QDialog instance
    ui = Ui_Dialog()  # Create an instance of the UI class
    ui.setupUi(dialog)  # Pass the QDialog instance to setupUi
    dialog.show()
    sys.exit(app.exec_())
